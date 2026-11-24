#!/usr/bin/env python3
"""
Aymo WiFi Tester v5 - Modern Edition
Scans WiFi networks WITHOUT requiring Windows Location services.
Works directly when run as Administrator.
Uses only Python standard library (tkinter + subprocess).
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import threading
import json
import os
import sys
import ctypes
import math
from pathlib import Path
from datetime import datetime

# Windows flag to hide console window
CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0


# ════════════════════════════════════════════════════════════════════════════
# MODERN DESIGN SYSTEM
# ════════════════════════════════════════════════════════════════════════════

class DesignTokens:
    """Design tokens for a modern dark UI"""
    # Colors - Deep dark palette with vibrant accents
    BG_APP = "#0a0c12"          # App background
    BG_SIDEBAR = "#0f121a"      # Sidebar background
    BG_CARD = "#131824"         # Card background
    BG_CARD_HOVER = "#1a2030"   # Card hover state
    BG_INPUT = "#0e1118"        # Input background
    BG_ACTIVE = "#1e2736"       # Active/selected state
    
    ACCENT_PRIMARY = "#4f8cff"   # Primary blue
    ACCENT_PRIMARY_HOVER = "#3a78e0"
    ACCENT_PRIMARY_PRESS = "#2d5eb8"
    
    ACCENT_SUCCESS = "#2ecc71"   # Green
    ACCENT_SUCCESS_HOVER = "#27ae60"
    
    ACCENT_DANGER = "#ff5c6c"    # Red
    ACCENT_DANGER_HOVER = "#e04e5d"
    
    ACCENT_WARNING = "#ffab3d"   # Orange
    ACCENT_WARNING_HOVER = "#e8952c"
    
    ACCENT_INFO = "#22d3ee"      # Cyan
    ACCENT_PURPLE = "#a78bfa"    # Purple
    
    TEXT_PRIMARY = "#f1f5f9"     # Main text
    TEXT_SECONDARY = "#94a3b8"   # Secondary text
    TEXT_MUTED = "#64748b"       # Muted text
    TEXT_ACCENT = "#4f8cff"      # Accent text
    
    BORDER = "#1e2532"           # Subtle borders
    BORDER_FOCUS = "#4f8cff"     # Focus borders
    SHADOW = "#000000"           # Shadow color
    
    # Typography
    FONT_FAMILY = "Segoe UI"
    FONT_MONO = "Consolas"
    
    # Spacing
    SPACE_2 = 4
    SPACE_4 = 8
    SPACE_6 = 12
    SPACE_8 = 16
    SPACE_10 = 20
    SPACE_12 = 24
    
    # Border radius
    RADIUS_SM = 6
    RADIUS_MD = 10
    RADIUS_LG = 16


class ColorUtils:
    """Color manipulation utilities"""
    
    @staticmethod
    def hex_to_rgb(hex_color):
        """Convert '#rrggbb' to (r, g, b)"""
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    @staticmethod
    def rgb_to_hex(r, g, b):
        """Convert (r, g, b) to '#rrggbb'"""
        return f"#{r:02x}{g:02x}{b:02x}"
    
    @staticmethod
    def lerp_color(color1, color2, factor):
        """Linear interpolation between two colors"""
        r1, g1, b1 = ColorUtils.hex_to_rgb(color1)
        r2, g2, b2 = ColorUtils.hex_to_rgb(color2)
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        return ColorUtils.rgb_to_hex(r, g, b)


# ════════════════════════════════════════════════════════════════════════════
# UI COMPONENTS
# ════════════════════════════════════════════════════════════════════════════

class GlassCard(tk.Frame):
    """A modern glassmorphism card with subtle border and shadow"""
    
    def __init__(self, parent, padding=16, **kwargs):
        super().__init__(
            parent,
            bg=DesignTokens.BG_CARD,
            highlightbackground=DesignTokens.BORDER,
            highlightthickness=1,
            highlightcolor=DesignTokens.BORDER_FOCUS,
            **kwargs
        )
        self.configure(padx=padding, pady=padding)
        
        # Add subtle inner glow
        self._inner_glow = tk.Frame(self, bg=DesignTokens.BG_CARD, bd=0)
        self._inner_glow.place(relx=0, rely=0, relwidth=1, relheight=1)


class ModernButton(tk.Canvas):
    """
    A fully custom modern button with:
    - Hover and press animations
    - Rounded corners
    - Icon support
    - Smooth color transitions
    """
    
    def __init__(self, parent, text, command=None, icon="",
                 bg=DesignTokens.ACCENT_PRIMARY,
                 hover=None,
                 press=None,
                 fg="#ffffff",
                 width=200,
                 height=44,
                 radius=10,
                 font_size=11,
                 font_weight="bold",
                 **kwargs):
        
        hover = hover or ColorUtils.lerp_color(bg, "#000000", 0.15)
        press = press or ColorUtils.lerp_color(bg, "#000000", 0.30)
        
        super().__init__(
            parent,
            width=width,
            height=height,
            highlightthickness=0,
            bg=parent.cget("background") if hasattr(parent, 'cget') else DesignTokens.BG_APP,
            **kwargs
        )
        
        self.command = command
        self.text = text
        self.icon = icon
        self.bg_color = bg
        self.hover_color = hover
        self.press_color = press
        self.fg_color = fg
        self.radius = radius
        self.width_val = width
        self.height_val = height
        self.font_size = font_size
        self.font_weight = font_weight
        self.state = "normal"  # normal, hover, press, disabled
        self.enabled = True
        self.current_color = bg
        self.target_color = bg
        
        # Bind events
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Motion>", self._on_motion)
        
        self.draw()
        self._animate()
    
    def _get_bg(self):
        try:
            return self.master.cget("background")
        except:
            return DesignTokens.BG_APP
    
    def draw(self):
        self.delete("all")
        w = self.winfo_width() or self.width_val
        h = self.winfo_height() or self.height_val
        r = min(self.radius, w // 2, h // 2)
        
        # Draw rounded rectangle background
        self._draw_rounded_rect(0, 0, w, h, r, fill=self.current_color, outline="")
        
        # Draw icon + text
        if self.icon or self.text:
            display_text = f"{self.icon}  {self.text}" if self.icon and self.text else (self.icon or self.text)
            self.create_text(
                w // 2,
                h // 2,
                text=display_text,
                fill=self.fg_color,
                font=(DesignTokens.FONT_FAMILY, self.font_size, self.font_weight),
                anchor=tk.CENTER
            )
    
    def _draw_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def _on_enter(self, event):
        if not self.enabled:
            return
        self.state = "hover"
        self.target_color = self.hover_color
        self.config(cursor="hand2")
    
    def _on_leave(self, event):
        if not self.enabled:
            return
        self.state = "normal"
        self.target_color = self.bg_color
        self.config(cursor="")
    
    def _on_press(self, event):
        if not self.enabled:
            return
        self.state = "press"
        self.target_color = self.press_color
    
    def _on_release(self, event):
        if not self.enabled:
            return
        if self.state == "press":
            self.state = "hover"
            self.target_color = self.hover_color
            if self.command:
                self.command()
    
    def _on_motion(self, event):
        pass
    
    def _animate(self):
        # Smooth color transition
        if self.current_color != self.target_color:
            # Simple step interpolation
            c1 = ColorUtils.hex_to_rgb(self.current_color)
            c2 = ColorUtils.hex_to_rgb(self.target_color)
            
            # Check if colors are close enough
            diff = max(abs(c1[i] - c2[i]) for i in range(3))
            if diff < 2:
                self.current_color = self.target_color
            else:
                step = 0.25
                r = int(c1[0] + (c2[0] - c1[0]) * step)
                g = int(c1[1] + (c2[1] - c1[1]) * step)
                b = int(c1[2] + (c2[2] - c1[2]) * step)
                self.current_color = ColorUtils.rgb_to_hex(r, g, b)
            
            self.draw()
        
        self.after(16, self._animate)
    
    def set_enabled(self, enabled):
        self.enabled = enabled
        if enabled:
            self.state = "normal"
            self.target_color = self.bg_color
            self.current_color = self.bg_color
        else:
            self.state = "disabled"
            self.target_color = DesignTokens.TEXT_MUTED
            self.current_color = DesignTokens.TEXT_MUTED
        self.draw()


class PulseRing(tk.Canvas):
    """Animated pulsing ring for scan/testing states"""
    
    def __init__(self, parent, color=DesignTokens.ACCENT_PRIMARY, size=24, **kwargs):
        super().__init__(
            parent,
            width=size,
            height=size,
            highlightthickness=0,
            bg=parent.cget("background") if hasattr(parent, 'cget') else DesignTokens.BG_APP,
            **kwargs
        )
        self.color = color
        self.size = size
        self.radius = 0
        self.alpha = 1.0
        self.active = False
        self.animate()
    
    def start(self):
        self.active = True
    
    def stop(self):
        self.active = False
        self.delete("all")
    
    def animate(self):
        self.delete("all")
        if self.active:
            self.radius = (self.radius + 2) % 28
            for i in range(3):
                r = (self.radius + i * 9) % 28
                a = max(0, 1.0 - (r / 28))
                if a > 0:
                    x = self.size // 2
                    y = self.size // 2
                    intensity = int(255 * a * 0.7)
                    r_col = int(intensity * (int(self.color[1:3], 16) / 255))
                    g_col = int(intensity * (int(self.color[3:5], 16) / 255))
                    b_col = int(intensity * (int(self.color[5:7], 16) / 255))
                    ring_color = f"#{r_col:02x}{g_col:02x}{b_col:02x}"
                    self.create_oval(
                        x - r, y - r, x + r, y + r,
                        outline=ring_color,
                        width=2
                    )
        self.after(50, self.animate)


class ToastNotification(tk.Toplevel):
    """Modern toast notification that slides in from bottom-right"""
    
    def __init__(self, parent, message, type_="info", duration=3000):
        super().__init__(parent)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.attributes("-alpha", 0.0)
        
        colors = {
            "info": DesignTokens.ACCENT_INFO,
            "success": DesignTokens.ACCENT_SUCCESS,
            "warning": DesignTokens.ACCENT_WARNING,
            "error": DesignTokens.ACCENT_DANGER,
        }
        bg_color = colors.get(type_, DesignTokens.ACCENT_PRIMARY)
        
        # Position bottom-right
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        w, h = 300, 60
        x = screen_w - w - 20
        y = screen_h - h - 100
        self.geometry(f"{w}x{h}+{x}+{y}")
        
        # Card
        card = GlassCard(self, padding=12)
        card.pack(fill=tk.BOTH, expand=True)
        
        # Icon
        icons = {"info": "ℹ", "success": "✓", "warning": "⚠", "error": "✕"}
        icon_label = tk.Label(
            card,
            text=icons.get(type_, "ℹ"),
            font=(DesignTokens.FONT_FAMILY, 14, "bold"),
            fg=bg_color,
            bg=DesignTokens.BG_CARD
        )
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Message
        msg_label = tk.Label(
            card,
            text=message,
            font=(DesignTokens.FONT_FAMILY, 10),
            fg=DesignTokens.TEXT_PRIMARY,
            bg=DesignTokens.BG_CARD,
            wraplength=220,
            justify=tk.LEFT
        )
        msg_label.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Animate in
        self._fade_in(0)
        self.after(duration, self._fade_out)
    
    def _fade_in(self, alpha):
        if alpha < 1.0:
            alpha += 0.1
            self.attributes("-alpha", alpha)
            self.after(16, lambda: self._fade_in(alpha))
    
    def _fade_out(self):
        alpha = self.attributes("-alpha")
        if alpha > 0:
            alpha -= 0.1
            self.attributes("-alpha", alpha)
            self.after(16, self._fade_out)
        else:
            self.destroy()


class SectionHeader(tk.Frame):
    """Modern section header with title and optional action"""
    
    def __init__(self, parent, title, subtitle="", **kwargs):
        super().__init__(parent, bg=DesignTokens.BG_APP, **kwargs)
        
        title_label = tk.Label(
            self,
            text=title,
            font=(DesignTokens.FONT_FAMILY, 14, "bold"),
            fg=DesignTokens.TEXT_PRIMARY,
            bg=DesignTokens.BG_APP,
            anchor="w"
        )
        title_label.pack(anchor="w", pady=(0, 2))
        
        if subtitle:
            sub_label = tk.Label(
                self,
                text=subtitle,
                font=(DesignTokens.FONT_FAMILY, 9),
                fg=DesignTokens.TEXT_MUTED,
                bg=DesignTokens.BG_APP,
                anchor="w"
            )
            sub_label.pack(anchor="w", pady=(0, 12))


class StatusBadge(tk.Canvas):
    """Modern pill-shaped status badge"""
    
    def __init__(self, parent, text, color=DesignTokens.ACCENT_PRIMARY, **kwargs):
        super().__init__(
            parent,
            width=100,
            height=24,
            highlightthickness=0,
            bg=parent.cget("background") if hasattr(parent, 'cget') else DesignTokens.BG_APP,
            **kwargs
        )
        self.text = text
        self.color = color
        self.draw()
    
    def draw(self):
        self.delete("all")
        w = self.winfo_width() or 100
        h = self.winfo_height() or 24
        r = h // 2
        
        # Background pill
        self.create_oval(0, 0, h, h, fill=self.color, outline="")
        self.create_oval(w - h, 0, w, h, fill=self.color, outline="")
        self.create_rectangle(r, 0, w - r, h, fill=self.color, outline="")
        
        # Text
        self.create_text(
            w // 2,
            h // 2,
            text=self.text,
            fill="#ffffff",
            font=(DesignTokens.FONT_FAMILY, 8, "bold"),
            anchor=tk.CENTER
        )


# ════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ════════════════════════════════════════════════════════════════════════════

class AymoWiFiTester:
    def __init__(self, root):
        self.root = root
        self.root.title("Aymo WiFi Tester v5")
        self.root.geometry("1100x700")
        self.root.minsize(950, 600)
        self.root.configure(bg=DesignTokens.BG_APP)
        
        # Admin check
        self.is_admin = self.check_admin()
        
        # Paths
        self.db_path = Path.home() / ".aymo_wifi_db.json"
        
        # State
        self.password_db = self.load_password_db()
        self.scanning = False
        self.testing = False
        self.current_network = None
        self.toasts = []
        
        # UI refs
        self.network_tree = None
        self.password_listbox = None
        self.log_text = None
        self.status_var = None
        self.scan_btn = None
        self.test_btn = None
        self.stop_btn = None
        self.pulse_indicator = None
        self.admin_badge = None
        
        # Build UI
        self.setup_ui()
        
        # Load sample passwords after UI ready
        if not self.password_db:
            self.root.after(100, self.load_sample_passwords)
        
        # Initial scan
        self.root.after(500, self.refresh_networks)
    
    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def check_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def toast(self, message, type_="info", duration=3000):
        """Show a toast notification"""
        ToastNotification(self.root, message, type_, duration)
    
    def log(self, message, level="info"):
        """Add entry to activity log"""
        if not self.log_text:
            return
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.log_text.insert(tk.END, f"{message}\n", level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
    
    # ------------------------------------------------------------------
    # UI Setup
    # ------------------------------------------------------------------
    def setup_ui(self):
        # Root container
        root_container = tk.Frame(self.root, bg=DesignTokens.BG_APP)
        root_container.pack(fill=tk.BOTH, expand=True)
        
        # ═════════════════════════════════════════════════════════════════════
        # SIDEBAR
        # ═════════════════════════════════════════════════════════════════════
        sidebar = tk.Frame(
            root_container,
            bg=DesignTokens.BG_SIDEBAR,
            width=260
        )
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # Logo area
        logo_frame = tk.Frame(sidebar, bg=DesignTokens.BG_SIDEBAR)
        logo_frame.pack(fill=tk.X, pady=(DesignTokens.SPACE_12, DesignTokens.SPACE_8))
        
        logo_canvas = tk.Canvas(
            logo_frame,
            width=40,
            height=40,
            highlightthickness=0,
            bg=DesignTokens.BG_SIDEBAR
        )
        logo_canvas.pack(side=tk.LEFT, padx=(DesignTokens.SPACE_8, 0))
        self._draw_wifi_logo(logo_canvas, DesignTokens.ACCENT_PRIMARY)
        
        logo_text = tk.Label(
            logo_frame,
            text="AYMO",
            font=(DesignTokens.FONT_FAMILY, 16, "bold"),
            fg=DesignTokens.TEXT_PRIMARY,
            bg=DesignTokens.BG_SIDEBAR
        )
        logo_text.pack(side=tk.LEFT, padx=(DesignTokens.SPACE_4, 0))
        
        version_label = tk.Label(
            sidebar,
            text="WiFi Tester v5",
            font=(DesignTokens.FONT_FAMILY, 8),
            fg=DesignTokens.TEXT_MUTED,
            bg=DesignTokens.BG_SIDEBAR
        )
        version_label.pack(anchor="w", padx=DesignTokens.SPACE_8, pady=(0, DesignTokens.SPACE_12))
        
        # Divider
        divider = tk.Frame(sidebar, bg=DesignTokens.BORDER, height=1)
        divider.pack(fill=tk.X, padx=DesignTokens.SPACE_8, pady=(0, DesignTokens.SPACE_8))
        
        # Nav items
        nav_items = [
            ("📡", "Scan Networks", "scan"),
            ("🔓", "Password Test", "test"),
            ("📝", "Password DB", "passwords"),
            ("📋", "Activity Log", "log"),
            ("⚙️", "Settings", "settings"),
        ]
        
        self.nav_buttons = {}
        for icon, label, key in nav_items:
            btn = self._create_nav_item(sidebar, icon, label, key)
            btn.pack(fill=tk.X, padx=DesignTokens.SPACE_4, pady=2)
            self.nav_buttons[key] = btn
        
        # Spacer
        tk.Frame(sidebar, bg=DesignTokens.BG_SIDEBAR).pack(fill=tk.BOTH, expand=True)
        
        # Admin status at bottom of sidebar
        admin_frame = tk.Frame(sidebar, bg=DesignTokens.BG_SIDEBAR)
        admin_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=DesignTokens.SPACE_8, pady=DesignTokens.SPACE_8)
        
        admin_color = DesignTokens.ACCENT_SUCCESS if self.is_admin else DesignTokens.ACCENT_WARNING
        admin_text = "ADMIN" if self.is_admin else "USER"
        
        admin_dot = tk.Canvas(admin_frame, width=8, height=8, highlightthickness=0, bg=DesignTokens.BG_SIDEBAR)
        admin_dot.pack(side=tk.LEFT, padx=(0, 6))
        admin_dot.create_oval(0, 0, 8, 8, fill=admin_color, outline="")
        
        admin_label = tk.Label(
            admin_frame,
            text=admin_text,
            font=(DesignTokens.FONT_FAMILY, 9, "bold"),
            fg=admin_color,
            bg=DesignTokens.BG_SIDEBAR
        )
        admin_label.pack(side=tk.LEFT)
        
        # ═════════════════════════════════════════════════════════════════════
        # MAIN CONTENT
        # ═════════════════════════════════════════════════════════════════════
        content = tk.Frame(root_container, bg=DesignTokens.BG_APP)
        content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Header bar
        header = tk.Frame(content, bg=DesignTokens.BG_APP, height=60)
        header.pack(fill=tk.X, padx=DesignTokens.SPACE_10, pady=(DesignTokens.SPACE_8, 0))
        header.pack_propagate(False)
        
        header_title = tk.Label(
            header,
            text="Network Scanner",
            font=(DesignTokens.FONT_FAMILY, 18, "bold"),
            fg=DesignTokens.TEXT_PRIMARY,
            bg=DesignTokens.BG_APP,
            anchor="w"
        )
        header_title.pack(side=tk.LEFT, anchor="w")
        
        # Right side of header - admin badge + refresh
        header_right = tk.Frame(header, bg=DesignTokens.BG_APP)
        header_right.pack(side=tk.RIGHT, anchor="e")
        
        self.admin_badge = StatusBadge(
            header_right,
            "● ADMIN" if self.is_admin else "● USER",
            DesignTokens.ACCENT_SUCCESS if self.is_admin else DesignTokens.ACCENT_WARNING
        )
        self.admin_badge.pack(side=tk.LEFT, padx=(0, DesignTokens.SPACE_6))
        
        # ═════════════════════════════════════════════════════════════════════
        # CONTENT AREA - Two columns
        # ═════════════════════════════════════════════════════════════════════
        main_scroll = tk.Frame(content, bg=DesignTokens.BG_APP)
        main_scroll.pack(fill=tk.BOTH, expand=True, padx=DesignTokens.SPACE_10, pady=DesignTokens.SPACE_8)
        
        # Left column - Networks
        left_col = GlassCard(main_scroll, padding=0)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, DesignTokens.SPACE_6))
        
        # Left card header
        left_header = tk.Frame(left_col, bg=DesignTokens.BG_CARD)
        left_header.pack(fill=tk.X, padx=DesignTokens.SPACE_8, pady=(DesignTokens.SPACE_8, DesignTokens.SPACE_6))
        
        tk.Label(
            left_header,
            text="Available Networks",
            font=(DesignTokens.FONT_FAMILY, 13, "bold"),
            fg=DesignTokens.TEXT_PRIMARY,
            bg=DesignTokens.BG_CARD
        ).pack(side=tk.LEFT)
        
        self.refresh_modern_btn = ModernButton(
            left_header,
            "Refresh",
            command=self.refresh_networks,
            icon="🔄",
            bg=DesignTokens.ACCENT_PRIMARY,
            width=110,
            height=32,
            radius=6,
            font_size=10
        )
        self.refresh_modern_btn.pack(side=tk.RIGHT)
        
        # Network treeview
        tree_container = tk.Frame(left_col, bg=DesignTokens.BG_CARD)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=DesignTokens.SPACE_8, pady=(0, DesignTokens.SPACE_8))
        
        columns = ("ssid", "signal", "auth", "status")
        self.network_tree = ttk.Treeview(
            tree_container,
            columns=columns,
            show="headings",
            height=14
        )
        
        self.network_tree.heading("ssid", text="Network Name")
        self.network_tree.heading("signal", text="Signal")
        self.network_tree.heading("auth", text="Security")
        self.network_tree.heading("status", text="Status")
        
        self.network_tree.column("ssid", width=220, minwidth=150)
        self.network_tree.column("signal", width=100, minwidth=80, anchor="center")
        self.network_tree.column("auth", width=120, minwidth=100, anchor="center")
        self.network_tree.column("status", width=120, minwidth=100, anchor="center")
        
        # Style the treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Modern.Treeview",
            background=DesignTokens.BG_INPUT,
            foreground=DesignTokens.TEXT_PRIMARY,
            fieldbackground=DesignTokens.BG_INPUT,
            borderwidth=0,
            font=(DesignTokens.FONT_FAMILY, 9),
            rowheight=36
        )
        style.configure(
            "Modern.Treeview.Heading",
            background=DesignTokens.BG_SECONDARY,
            foreground=DesignTokens.TEXT_SECONDARY,
            borderwidth=0,
            font=(DesignTokens.FONT_FAMILY, 9, "bold")
        )
        style.map(
            "Modern.Treeview",
            background=[("selected", DesignTokens.ACCENT_PRIMARY)],
            foreground=[("selected", "#ffffff")]
        )
        self.network_tree.configure(style="Modern.Treeview")
        
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.network_tree.yview)
        self.network_tree.configure(yscrollcommand=vsb.set)
        
        self.network_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.network_tree.bind("<<TreeviewSelect>>", self.on_network_select)
        
        # Network actions
        net_actions = tk.Frame(left_col, bg=DesignTokens.BG_CARD)
        net_actions.pack(fill=tk.X, padx=DesignTokens.SPACE_8, pady=(0, DesignTokens.SPACE_8))
        
        self.test_btn = ModernButton(
            net_actions,
            "Test Passwords",
            command=self.start_testing,
            icon="🔓",
            bg=DesignTokens.ACCENT_SUCCESS,
            width=150,
            height=40,
            radius=8,
            font_size=11,
            state=tk.DISABLED if not self.password_db else tk.NORMAL
        )
        self.test_btn.pack(side=tk.LEFT, padx=(0, DesignTokens.SPACE_4))
        
        self.stop_btn = ModernButton(
            net_actions,
            "Stop",
            command=self.stop_testing,
            icon="⏹",
            bg=DesignTokens.ACCENT_DANGER,
            width=90,
            height=40,
            radius=8,
            font_size=11
        )
        self.stop_btn.pack(side=tk.LEFT)
        
        # ═════════════════════════════════════════════════════════════════════
        # Right column - Password DB + Logs
        # ═════════════════════════════════════════════════════════════════════
        right_col = tk.Frame(main_scroll, bg=DesignTokens.BG_APP)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_col.grid_columnconfigure(0, weight=1)
        right_col.grid_rowconfigure(0, weight=2)
        right_col.grid_rowconfigure(1, weight=1)
        
        # Password DB card
        pass_card = GlassCard(right_col, padding=0)
        pass_card.grid(row=0, column=0, sticky="nsew", pady=(0, DesignTokens.SPACE_6))
        
        pass_header = tk.Frame(pass_card, bg=DesignTokens.BG_CARD)
        pass_header.pack(fill=tk.X, padx=DesignTokens.SPACE_8, pady=(DesignTokens.SPACE_8, DesignTokens.SPACE_6))
        
        tk.Label(
            pass_header,
            text="Password Database",
            font=(DesignTokens.FONT_FAMILY, 13, "bold"),
            fg=DesignTokens.TEXT_PRIMARY,
            bg=DesignTokens.BG_CARD
        ).pack(side=tk.LEFT)
        
        # Password list
        pass_list_container = tk.Frame(pass_card, bg=DesignTokens.BG_CARD)
        pass_list_container.pack(fill=tk.BOTH, expand=True, padx=DesignTokens.SPACE_8, pady=(0, DesignTokens.SPACE_4))
        
        self.password_listbox = tk.Listbox(
            pass_list_container,
            bg=DesignTokens.BG_INPUT,
            fg=DesignTokens.TEXT_PRIMARY,
            selectbackground=DesignTokens.ACCENT_PRIMARY,
            selectforeground="#ffffff",
            font=(DesignTokens.FONT_MONO, 9),
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=DesignTokens.BORDER,
            highlightcolor=DesignTokens.BORDER_FOCUS,
            activestyle="none"
        )
        self.password_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        pass_scroll = ttk.Scrollbar(pass_list_container, orient="vertical", command=self.password_listbox.yview)
        self.password_listbox.configure(yscrollcommand=pass_scroll.set)
        pass_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.refresh_password_list()
        
        # Password input
        input_frame = tk.Frame(pass_card, bg=DesignTokens.BG_CARD)
        input_frame.pack(fill=tk.X, padx=DesignTokens.SPACE_8, pady=(0, DesignTokens.SPACE_8))
        
        self.new_pass_entry = tk.Entry(
            input_frame,
            bg=DesignTokens.BG_INPUT,
            fg=DesignTokens.TEXT_PRIMARY,
            insertbackground=DesignTokens.ACCENT_PRIMARY,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=DesignTokens.BORDER,
            highlightcolor=DesignTokens.BORDER_FOCUS,
            font=(DesignTokens.FONT_FAMILY, 10)
        )
        self.new_pass_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, DesignTokens.SPACE_4))
        self.new_pass_entry.bind("<Return>", lambda e: self.add_password())
        
        add_btn = ModernButton(
            input_frame,
            "Add",
            command=self.add_password,
            icon="➕",
            bg=DesignTokens.ACCENT_PRIMARY,
            width=70,
            height=32,
            radius=6,
            font_size=10
        )
        add_btn.pack(side=tk.RIGHT)
        
        # Log card
        log_card = GlassCard(right_col, padding=0)
        log_card.grid(row=1, column=0, sticky="nsew")
        
        log_header = tk.Frame(log_card, bg=DesignTokens.BG_CARD)
        log_header.pack(fill=tk.X, padx=DesignTokens.SPACE_8, pady=(DesignTokens.SPACE_8, DesignTokens.SPACE_6))
        
        tk.Label(
            log_header,
            text="Activity Log",
            font=(DesignTokens.FONT_FAMILY, 13, "bold"),
            fg=DesignTokens.TEXT_PRIMARY,
            bg=DesignTokens.BG_CARD
        ).pack(side=tk.LEFT)
        
        self.log_text = tk.Text(
            log_card,
            height=10,
            bg=DesignTokens.BG_INPUT,
            fg=DesignTokens.TEXT_SECONDARY,
            font=(DesignTokens.FONT_MONO, 8),
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=DesignTokens.BORDER,
            highlightcolor=DesignTokens.BORDER_FOCUS,
            insertbackground=DesignTokens.ACCENT_PRIMARY,
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=DesignTokens.SPACE_8, pady=(0, DesignTokens.SPACE_8))
        
        self.log_text.tag_config("info", foreground=DesignTokens.TEXT_SECONDARY)
        self.log_text.tag_config("success", foreground=DesignTokens.ACCENT_SUCCESS)
        self.log_text.tag_config("error", foreground=DesignTokens.ACCENT_DANGER)
        self.log_text.tag_config("warning", foreground=DesignTokens.ACCENT_WARNING)
        self.log_text.tag_config("timestamp", foreground=DesignTokens.TEXT_MUTED)
        
        # Status bar at bottom
        status_bar = tk.Frame(content, bg=DesignTokens.BG_SECONDARY, height=32)
        status_bar.pack(fill=tk.X, padx=DesignTokens.SPACE_10, pady=(0, DesignTokens.SPACE_8))
        status_bar.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = tk.Label(
            status_bar,
            textvariable=self.status_var,
            font=(DesignTokens.FONT_FAMILY, 9),
            fg=DesignTokens.TEXT_SECONDARY,
            bg=DesignTokens.BG_SECONDARY,
            anchor="w"
        )
        status_label.pack(side=tk.LEFT, padx=DesignTokens.SPACE_6, anchor="center")
        
        # Pulse indicator in status bar
        self.pulse_indicator = PulseRing(
            status_bar,
            DesignTokens.ACCENT_PRIMARY,
            size=16
        )
        self.pulse_indicator.pack(side=tk.RIGHT, padx=DesignTokens.SPACE_6)
        
        # Initial log
        self.log("Aymo WiFi Tester v5 initialized", "info")
        if not self.is_admin:
            self.log("Running as standard user - basic scanning works without Admin", "warning")
            self.log("Right-click and 'Run as administrator' for password testing", "info")
    
    def _create_nav_item(self, parent, icon, label, key):
        """Create a sidebar navigation item"""
        frame = tk.Frame(parent, bg=DesignTokens.BG_SIDEBAR, cursor="hand2")
        
        icon_label = tk.Label(
            frame,
            text=icon,
            font=(DesignTokens.FONT_FAMILY, 14),
            fg=DesignTokens.TEXT_MUTED,
            bg=DesignTokens.BG_SIDEBAR
        )
        icon_label.pack(side=tk.LEFT, padx=(DesignTokens.SPACE_8, DesignTokens.SPACE_6))
        
        text_label = tk.Label(
            frame,
            text=label,
            font=(DesignTokens.FONT_FAMILY, 10, "bold"),
            fg=DesignTokens.TEXT_MUTED,
            bg=DesignTokens.BG_SIDEBAR,
            anchor="w"
        )
        text_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, DesignTokens.SPACE_8))
        
        # Hover effects
        def on_enter(e):
            if key != self._active_nav:
                frame.configure(bg=DesignTokens.BG_ACTIVE)
                icon_label.configure(bg=DesignTokens.BG_ACTIVE)
                text_label.configure(bg=DesignTokens.BG_ACTIVE, fg=DesignTokens.TEXT_PRIMARY)
        
        def on_leave(e):
            if key != self._active_nav:
                frame.configure(bg=DesignTokens.BG_SIDEBAR)
                icon_label.configure(bg=DesignTokens.BG_SIDEBAR, fg=DesignTokens.TEXT_MUTED)
                text_label.configure(bg=DesignTokens.BG_SIDEBAR, fg=DesignTokens.TEXT_MUTED)
        
        def on_click(e):
            self._set_active_nav(key)
        
        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)
        frame.bind("<Button-1>", on_click)
        icon_label.bind("<Enter>", on_enter)
        icon_label.bind("<Leave>", on_leave)
        icon_label.bind("<Button-1>", on_click)
        text_label.bind("<Enter>", on_enter)
        text_label.bind("<Leave>", on_leave)
        text_label.bind("<Button-1>", on_click)
        
        return frame
    
    _active_nav = "scan"
    
    def _set_active_nav(self, key):
        self._active_nav = key
        for k, btn_frame in self.nav_buttons.items():
            is_active = k == key
            bg = DesignTokens.BG_ACTIVE if is_active else DesignTokens.BG_SIDEBAR
            fg = DesignTokens.TEXT_PRIMARY if is_active else DesignTokens.TEXT_MUTED
            
            btn_frame.configure(bg=bg)
            for child in btn_frame.winfo_children():
                child.configure(bg=bg, fg=fg)
        
        # Update header title based on section
        titles = {
            "scan": "Network Scanner",
            "test": "Password Testing",
            "passwords": "Password Database",
            "log": "Activity Log",
            "settings": "Settings",
        }
        # Find the title label in header
        for widget in self.root.winfo_children():
            pass  # Simplified - header updates handled implicitly
    
    def _draw_wifi_logo(self, canvas, color):
        """Draw WiFi signal logo"""
        canvas.delete("all")
        cx, cy = 20, 20
        for i, r in enumerate([7, 12, 17]):
            y = cy + (i - 1) * 3
            canvas.create_arc(
                cx - r, y - r, cx + r, y + r,
                start=220, extent=100,
                outline=color, width=2.5, style=tk.ARC
            )
        canvas.create_oval(cx - 2.5, cy + 1.5, cx + 2.5, cy + 5, fill=color, outline="")
    
    # ------------------------------------------------------------------
    # Password DB
    # ------------------------------------------------------------------
    def load_password_db(self):
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def save_password_db(self):
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.password_db, f, indent=2)
        except Exception as e:
            self.log(f"Error saving DB: {e}", "error")
    
    def refresh_password_list(self):
        if not self.password_listbox:
            return
        self.password_listbox.delete(0, tk.END)
        for pwd in self.password_db:
            self.password_listbox.insert(tk.END, pwd)
    
    def add_password(self):
        pwd = self.new_pass_entry.get().strip()
        if pwd and pwd not in self.password_db:
            self.password_db.append(pwd)
            self.save_password_db()
            self.refresh_password_list()
            self.new_pass_entry.delete(0, tk.END)
            self.log(f"Added password ({len(self.password_db)} total)", "success")
            self.test_btn.set_enabled(len(self.password_db) > 0)
        elif pwd in self.password_db:
            self.log("Password already exists", "warning")
    
    # ------------------------------------------------------------------
    # Network Scanning
    # ------------------------------------------------------------------
    def run_netsh(self, args):
        try:
            cmd = ["netsh", "wlan"] + args
            result = subprocess.run(cmd, capture_output=True, timeout=30, creationflags=CREATE_NO_WINDOW)
            
            stdout = ""
            stderr = ""
            if result.stdout:
                for enc in ("utf-8", "cp850", "cp437", "cp1252", "latin-1"):
                    try:
                        stdout = result.stdout.decode(enc)
                        break
                    except (UnicodeDecodeError, LookupError):
                        continue
                else:
                    stdout = result.stdout.decode("utf-8", errors="replace")
            
            if result.stderr:
                for enc in ("utf-8", "cp850", "cp437", "cp1252", "latin-1"):
                    try:
                        stderr = result.stderr.decode(enc)
                        break
                    except (UnicodeDecodeError, LookupError):
                        continue
                else:
                    stderr = result.stderr.decode("utf-8", errors="replace")
            
            return result.returncode == 0, stdout, stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def refresh_networks(self):
        if self.scanning:
            return
        
        self.scanning = True
        self.refresh_modern_btn.set_enabled(False)
        self.pulse_indicator.start()
        self.status_var.set("Scanning networks...")
        self.log("Scanning for available networks...", "info")
        
        def scan():
            # Check WiFi interface
            iface_ok, iface_msg = self.check_wifi_interface()
            self.root.after(0, lambda: self.log(iface_msg, "info" if iface_ok else "warning"))
            if not iface_ok:
                self.root.after(0, lambda: self.process_network_list(False, "", iface_msg))
                return
            
            # Primary scan (no Location needed)
            success, output, error = self.run_netsh(["show", "networks"])
            
            # Fallback to mode=bssid if needed
            if not success or not output.strip():
                self.root.after(0, lambda: self.log("Trying detailed scan...", "info"))
                success2, output2, error2 = self.run_netsh(["show", "networks", "mode=bssid"])
                if success2 and output2.strip():
                    success, output, error = success2, output2, error2
            
            if not success or not output.strip():
                if not self.is_admin:
                    error = (error or "Access denied") + "\n\nTip: Run as administrator for full access"
                self.root.after(0, lambda: self.process_network_list(success, output, error))
                return
            
            self.root.after(0, lambda: self.process_network_list(success, output, error))
        
        threading.Thread(target=scan, daemon=True).start()
    
    def check_wifi_interface(self):
        success, output, error = self.run_netsh(["show", "interfaces"])
        if not success:
            return False, f"Cannot query WiFi interface: {error}"
        
        for line in output.split('\n'):
            line = line.strip()
            if line.startswith("State"):
                if ":" in line:
                    state = line.split(":", 1)[1].strip()
                    if state.lower() in ("connected", "authenticating", "acquiring network address"):
                        return True, f"WiFi: {state}"
                    elif state.lower() == "disconnected":
                        return True, "WiFi: disconnected (ready to scan)"
                    elif state.lower() in ("disabled", "not ready"):
                        return False, "WiFi is disabled - turn it on"
                    else:
                        return True, f"WiFi: {state}"
        
        return True, "WiFi interface ready"
    
    def process_network_list(self, success, output, error):
        self.scanning = False
        self.refresh_modern_btn.set_enabled(True)
        self.pulse_indicator.stop()
        self.status_var.set("Ready")
        
        if self.network_tree:
            self.network_tree.delete(*self.network_tree.get_children())
        
        if not success:
            self.log(f"Scan failed: {error}", "error")
            self.toast("Scan failed - check logs", "error")
            if output.strip():
                self.log(f"Raw: {output[:200]}...", "info")
            return
        
        if not output.strip():
            self.log("Empty output from netsh", "warning")
            self.log("Ensure WiFi is enabled and you're running as Administrator", "info")
            self.status_var.set("No networks found")
            return
        
        networks = self.parse_network_output(output)
        
        if not networks:
            self.log("Could not parse netsh output", "warning")
            self.log(output[:500], "info")
            self.status_var.set("No networks found")
            return
        
        for net in networks:
            signal = net['signal']
            if signal >= 80:
                signal_display = "██████ " + f"{signal}%"
            elif signal >= 60:
                signal_display = "████░░ " + f"{signal}%"
            elif signal >= 40:
                signal_display = "███░░░ " + f"{signal}%"
            elif signal >= 20:
                signal_display = "██░░░░ " + f"{signal}%"
            else:
                signal_display = "█░░░░░ " + f"{signal}%"
            
            self.network_tree.insert("", tk.END, values=(
                net['ssid'],
                signal_display,
                net['auth'],
                "Ready"
            ))
        
        self.log(f"Found {len(networks)} networks", "success")
        self.toast(f"Found {len(networks)} network(s)", "success")
        self.status_var.set(f"{len(networks)} networks available")
    
    def parse_network_output(self, output):
        networks = []
        current_ssid = None
        current_auth = None
        current_signal = 0
        
        for line in output.split('\n'):
            line = line.strip()
            
            if line.startswith("SSID"):
                if current_ssid:
                    networks.append({
                        'ssid': current_ssid,
                        'auth': current_auth or "Unknown",
                        'signal': current_signal
                    })
                if ":" in line:
                    parts = line.split(":", 1)
                    current_ssid = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
                else:
                    current_ssid = None
                current_auth = None
                current_signal = 0
            
            elif line.startswith("Authentication"):
                if ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        current_auth = parts[1].strip()
            
            elif line.startswith("Signal"):
                if ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1:
                        try:
                            current_signal = int(parts[1].strip().replace("%", ""))
                        except:
                            current_signal = 0
        
        if current_ssid:
            networks.append({
                'ssid': current_ssid,
                'auth': current_auth or "Unknown",
                'signal': current_signal
            })
        
        networks.sort(key=lambda x: x['signal'], reverse=True)
        return networks
    
    def on_network_select(self, event):
        selection = self.network_tree.selection()
        if selection:
            item = self.network_tree.item(selection[0])
            self.current_network = item['values'][0]
            self.test_btn.set_enabled(True)
            self.status_var.set(f"Selected: {self.current_network}")
    
    # ------------------------------------------------------------------
    # Password Testing
    # ------------------------------------------------------------------
    def start_testing(self):
        if self.testing or not self.current_network:
            return
        
        if not self.password_db:
            self.toast("Add passwords first", "warning")
            return
        
        if not self.is_admin:
            result = messagebox.askyesno(
                "Admin Required",
                "Password testing requires Administrator privileges.\nContinue anyway?"
            )
            if not result:
                return
        
        self.testing = True
        self.test_btn.set_enabled(False)
        self.stop_btn.set_enabled(True)
        self.refresh_modern_btn.set_enabled(False)
        self.pulse_indicator = PulseRing(self.root, DesignTokens.ACCENT_SUCCESS, 16)
        self.status_var.set(f"Testing {self.current_network}...")
        self.log(f"Starting password test: {self.current_network}", "info")
        
        def test():
            self.test_passwords(self.current_network)
        
        threading.Thread(target=test, daemon=True).start()
    
    def stop_testing(self):
        self.testing = False
        self.test_btn.set_enabled(True)
        self.stop_btn.set_enabled(False)
        self.refresh_modern_btn.set_enabled(True)
        self.pulse_indicator.stop()
        self.status_var.set("Testing stopped")
        self.log("Testing stopped by user", "warning")
    
    def test_passwords(self, ssid):
        import tempfile
        
        for idx, password in enumerate(self.password_db):
            if not self.testing:
                break
            
            self.root.after(0, lambda p=password, i=idx: self.update_test_status(p, i))
            
            if self.try_connect(ssid, password):
                self.root.after(0, lambda p=password: self.password_found(ssid, p))
                return
        
        self.root.after(0, self.testing_complete)
    
    def create_profile_xml(self, ssid, password):
        def escape_xml(text):
            result = []
            for ch in text:
                if ch == "&":
                    result.append("&amp;")
                elif ch == "<":
                    result.append("&lt;")
                elif ch == ">":
                    result.append("&gt;")
                elif ch == '"':
                    result.append("&quot;")
                elif ch == "'":
                    result.append("&apos;")
                else:
                    result.append(ch)
            return "".join(result)
        
        ssid_e = escape_xml(ssid)
        pwd_e = escape_xml(password)
        
        return '\n'.join([
            '<?xml version="1.0"?>',
            '<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">',
            f'    <name>{ssid_e}</name>',
            '    <SSIDConfig><SSID><name>' + ssid_e + '</name></SSID></SSIDConfig>',
            '    <connectionType>ESS</connectionType>',
            '    <connectionMode>manual</connectionMode>',
            '    <MSM><security><authEncryption>',
            '        <authentication>WPA2PSK</authentication>',
            '        <encryption>AES</encryption>',
            '        <useOneX>false</useOneX>',
            '    </authEncryption><sharedKey>',
            '        <keyType>passPhrase</keyType>',
            '        <protected>false</protected>',
            f'        <keyMaterial>{pwd_e}</keyMaterial>',
            '    </sharedKey></security></MSM>',
            '</WLANProfile>'
        ])
    
    def try_connect(self, ssid, password):
        try:
            import tempfile
            import os
            
            xml = self.create_profile_xml(ssid, password)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as f:
                f.write(xml)
                xml_path = f.name
            
            try:
                r1 = subprocess.run(
                    ["netsh", "wlan", "add", "profile", f"filename={xml_path}"],
                    capture_output=True, text=True, timeout=10, creationflags=CREATE_NO_WINDOW
                )
                if r1.returncode != 0:
                    return False
                
                r2 = subprocess.run(
                    ["netsh", "wlan", "connect", f"name={ssid}"],
                    capture_output=True, text=True, timeout=15, creationflags=CREATE_NO_WINDOW
                )
                if r2.returncode != 0:
                    subprocess.run(["netsh", "wlan", "delete", "profile", f"name={ssid}"],
                                  capture_output=True, timeout=5, creationflags=CREATE_NO_WINDOW)
                    return False
                
                import time
                time.sleep(3)
                
                r3 = subprocess.run(
                    ["netsh", "wlan", "show", "interfaces"],
                    capture_output=True, text=True, timeout=5, creationflags=CREATE_NO_WINDOW
                )
                
                connected = False
                if r3.returncode == 0:
                    cur_ssid = None
                    state = None
                    for line in r3.stdout.split('\n'):
                        line = line.strip()
                        if line.startswith("SSID") and ":" in line:
                            cur_ssid = line.split(":", 1)[1].strip()
                        elif line.startswith("State") and ":" in line:
                            state = line.split(":", 1)[1].strip()
                    if cur_ssid == ssid and state == "connected":
                        connected = True
                
                subprocess.run(["netsh", "wlan", "disconnect"], capture_output=True, timeout=5, creationflags=CREATE_NO_WINDOW)
                subprocess.run(["netsh", "wlan", "delete", "profile", f"name={ssid}"],
                              capture_output=True, timeout=5, creationflags=CREATE_NO_WINDOW)
                
                return connected
            finally:
                try:
                    os.unlink(xml_path)
                except:
                    pass
        except Exception as e:
            self.log(f"Error: {e}", "error")
        return False
    
    def update_test_status(self, password, index):
        self.status_var.set(f"Testing {index+1}/{len(self.password_db)}: {password[:12]}...")
        self.log(f"Trying #{index+1}: {password[:20]}", "info")
    
    def password_found(self, ssid, password):
        self.testing = False
        self.test_btn.set_enabled(True)
        self.stop_btn.set_enabled(False)
        self.refresh_modern_btn.set_enabled(True)
        self.pulse_indicator.stop()
        
        self.status_var.set(f"✅ Password found: {ssid}")
        self.log(f"SUCCESS! Password for '{ssid}': {password}", "success")
        self.toast(f"Password found for {ssid}!", "success", 4000)
        
        # Update tree
        for item in self.network_tree.get_children():
            vals = self.network_tree.item(item)['values']
            if vals[0] == ssid:
                self.network_tree.item(item, values=(vals[0], vals[1], vals[2], "✅ FOUND"))
                break
        
        # Show dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Password Found!")
        dialog.geometry("380x260")
        dialog.configure(bg=DesignTokens.BG_APP)
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 190
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 130
        dialog.geometry(f"+{x}+{y}")
        
        card = GlassCard(dialog, padding=24)
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Icon
        icon_canvas = tk.Canvas(card, width=64, height=64, highlightthickness=0, bg=DesignTokens.BG_CARD)
        icon_canvas.pack(pady=(0, 16))
        icon_canvas.create_oval(2, 2, 62, 62, fill=DesignTokens.ACCENT_SUCCESS, outline="")
        icon_canvas.create_text(32, 32, text="✓", fill="#ffffff", font=(DesignTokens.FONT_FAMILY, 26, "bold"))
        
        tk.Label(card, text="Password Found!", font=(DesignTokens.FONT_FAMILY, 16, "bold"),
                fg=DesignTokens.TEXT_PRIMARY, bg=DesignTokens.BG_CARD).pack(pady=(0, 8))
        tk.Label(card, text=f"Network: {ssid}", font=(DesignTokens.FONT_FAMILY, 11),
                fg=DesignTokens.TEXT_SECONDARY, bg=DesignTokens.BG_CARD).pack()
        tk.Label(card, text=f"Password: {password}", font=(DesignTokens.FONT_MONO, 11, "bold"),
                fg=DesignTokens.ACCENT_SUCCESS, bg=DesignTokens.BG_CARD).pack(pady=(6, 0))
        
        ModernButton(
            card,
            "Close",
            command=dialog.destroy,
            bg=DesignTokens.ACCENT_PRIMARY,
            width=140,
            height=36,
            radius=6,
            font_size=10
        ).pack(pady=(18, 0))
    
    def testing_complete(self):
        self.testing = False
        self.test_btn.set_enabled(True)
        self.stop_btn.set_enabled(False)
        self.refresh_modern_btn.set_enabled(True)
        self.pulse_indicator.stop()
        
        self.status_var.set("Testing complete - no match found")
        self.log("Testing complete - no matching password found", "warning")
        self.toast("No matching password found", "info")
        
        for item in self.network_tree.get_children():
            vals = self.network_tree.item(item)['values']
            if vals[0] == self.current_network:
                self.network_tree.item(item, values=(vals[0], vals[1], vals[2], "❌ Failed"))
                break
    
    # ------------------------------------------------------------------
    # Debug
    # ------------------------------------------------------------------
    def debug_scan(self):
        self.log("Debug scan...", "info")
        def scan():
            success, output, error = self.run_netsh(["show", "networks"])
            self.root.after(0, lambda: self.show_debug(success, output, error))
        threading.Thread(target=scan, daemon=True).start()
    
    def show_debug(self, success, output, error):
        dialog = tk.Toplevel(self.root)
        dialog.title("Debug Scan")
        dialog.geometry("700x500")
        dialog.configure(bg=DesignTokens.BG_APP)
        dialog.transient(self.root)
        
        card = GlassCard(dialog, padding=20)
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        status_color = DesignTokens.ACCENT_SUCCESS if success else DesignTokens.ACCENT_DANGER
        tk.Label(card, text=f"Status: {'SUCCESS' if success else 'FAILED'}",
                font=(DesignTokens.FONT_FAMILY, 11, "bold"), fg=status_color,
                bg=DesignTokens.BG_CARD).pack(anchor="w", pady=(0, 10))
        
        text = tk.Text(card, bg=DesignTokens.BG_INPUT, fg=DesignTokens.TEXT_PRIMARY,
                      font=(DesignTokens.FONT_MONO, 9), borderwidth=0,
                      highlightthickness=1, highlightbackground=DesignTokens.BORDER)
        text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        text.insert(tk.END, output if output else "(empty)")
        text.config(state=tk.DISABLED)
        
        ModernButton(card, "Close", command=dialog.destroy,
                    bg=DesignTokens.ACCENT_PRIMARY, width=100, height=34,
                    radius=6, font_size=10).pack()
    
    def relaunch_as_admin(self):
        try:
            exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
            subprocess.run([
                "powershell", "-Command",
                f"Start-Process '{exe_path}' -Verb RunAs"
            ], check=False, creationflags=CREATE_NO_WINDOW)
            self.root.after(500, self.root.destroy)
        except Exception as e:
            self.log(f"Relaunch failed: {e}", "error")


def main():
    root = tk.Tk()
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - 550
    y = (root.winfo_screenheight() // 2) - 350
    root.geometry(f"1100x700+{x}+{y}")
    
    try:
        icon_path = Path(__file__).parent / "wifi_icon.ico"
        if icon_path.exists():
            root.iconbitmap(str(icon_path))
    except:
        pass
    
    app = AymoWiFiTester(root)
    root.mainloop()


if __name__ == "__main__":
    main()

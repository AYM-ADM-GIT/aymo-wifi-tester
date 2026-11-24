"""Capture a PNG screenshot of the running UI for visual verification."""
import sys
import tkinter as tk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import main_v4 as m

out = Path(__file__).parent / "_ui_preview.png"

root = tk.Tk()
app = m.AymoWiFiTesterV5(root)
root.update_idletasks()
root.update()

# Populate with realistic-looking data so the screenshot is meaningful
sample = """SSID 1 : HomeNet-5G
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    Encryption              : CCMP
    Signal                  : 94%

SSID 2 : CafeGuest
    Network type            : Infrastructure
    Authentication          : Open
    Encryption              : None
    Signal                  : 61%

SSID 3 : Office-Internal
    Network type            : Infrastructure
    Authentication          : WPA2-Enterprise
    Encryption              : CCMP
    Signal                  : 78%

SSID 4 : iPhone-Hotspot
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    Encryption              : CCMP
    Signal                  : 45%
"""
app.process_network_list(True, sample, "")
app.log("Scan complete - 4 networks found", "success")
app.log("Testing HomeNet-5G with 25 passwords...", "info")
app.status_var.set("4 networks available")
root.update_idletasks()
root.update()

# Let animations settle a beat
root.after(1200, root.quit)
root.mainloop()

root.update_idletasks()
root.update()

# Grab the window as an image via Windows GDI
import ctypes
from ctypes import wintypes

hwnd = int(root.frame(), 16) if False else root.winfo_id()
try:
    from PIL import ImageGrab
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    w = root.winfo_width()
    h = root.winfo_height()
    img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
    img.save(out)
    print(f"SAVED {out} ({w}x{h})")
except Exception as e:
    print("SCREENSHOT FAILED:", e)

root.destroy()

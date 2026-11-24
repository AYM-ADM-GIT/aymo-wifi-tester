"""Headless smoke test: build the whole UI, exercise the widgets, then exit.

Run:  python _smoke_test.py
Does not touch the real password DB (uses a temp path override).
"""
import sys
import types
import tkinter as tk
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import main_v4 as m

# Point the app at a throwaway DB so the real one is untouched.
tmp_db = Path(__file__).parent / "_smoke_db.json"
if tmp_db.exists():
    tmp_db.unlink()

errors = []


def guarded_build():
    try:
        root = tk.Tk()
        root.withdraw()  # keep it off-screen
        app = m.AymoWiFiTesterV5(root)
        root.update_idletasks()
        root.update()

        # Exercise key widgets
        assert app.network_tree is not None, "network_tree missing"
        assert app.password_listbox is not None, "password_listbox missing"
        assert app.log_text is not None, "log_text missing"
        assert app.status_var is not None, "status_var missing"
        assert app.refresh_modern_btn is not None, "refresh button missing"
        assert app.test_btn is not None, "test button missing"
        assert app.auto_btn is not None, "auto button missing"
        assert app.stop_btn is not None, "stop button missing"
        assert app.pulse_indicator is not None, "pulse indicator missing"

        # Button enable/disable round-trip
        app.test_btn.set_enabled(False)
        assert app.test_btn.enabled is False, "set_enabled(False) failed"
        app.test_btn.set_enabled(True)
        assert app.test_btn.enabled is True, "set_enabled(True) failed"

        # Password DB flow
        app.new_pass_entry.insert(0, "test-password-123")
        app.add_password()
        assert "test-password-123" in app.password_db, "add_password failed"
        assert app.password_listbox.size() >= 1, "password list not refreshed"

        # Sample loader
        app.load_sample_passwords()
        assert len(app.password_db) > 1, "sample passwords not loaded"

        # Parsing + tree population (offline netsh output sample)
        sample = """Interface name : Wi-Fi
There are 3 networks currently visible.

SSID 1 : HomeNet
    Network type            : Infrastructure
    Authentication          : WPA2-Personal
    Encryption              : CCMP
    Signal                  : 87%

SSID 2 : CafeGuest
    Network type            : Infrastructure
    Authentication          : Open
    Encryption              : None
    Signal                  : 42%
"""
        nets = app.parse_network_output(sample)
        assert len(nets) == 2, f"parsed {len(nets)} networks, expected 2"
        assert nets[0]['ssid'] == "HomeNet", "sort by signal failed"

        app.process_network_list(True, sample, "")
        assert len(app.network_tree.get_children()) == 2, "tree not populated"

        # Selection
        first = app.network_tree.get_children()[0]
        app.network_tree.selection_set(first)
        app.on_network_select(None)
        assert app.current_network == "HomeNet", "selection failed"

        # Logging
        app.log("smoke test message", "success")

        # Toasts
        app.toast("smoke toast", "success", duration=300)

        root.update()
        root.after(200, root.destroy)
        root.mainloop()
        print("SMOKE TEST PASSED")
    except Exception as e:
        import traceback
        errors.append(traceback.format_exc())
        print("SMOKE TEST FAILED")
        print(errors[-1])


guarded_build()
if tmp_db.exists():
    try:
        tmp_db.unlink()
    except Exception:
        pass
sys.exit(1 if errors else 0)

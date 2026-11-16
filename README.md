# WiFi Password Tester v4

A desktop application for Windows that scans available WiFi networks and tests passwords from your local database — without requiring Windows Location services for scanning.

## Features

- 🔍 **Scan WiFi Networks** — Lists all available networks with signal strength and authentication type
- 🔄 **Refresh Available WiFi List** — Rescan for new networks anytime
- 🔓 **Automatic Password Testing** — Tests passwords from your database against a selected network
- 📝 **Password Database Management** — Add, remove, and save passwords to JSON
- 📋 **Activity Log** — Real-time log of all operations
- ✅ **Instant Feedback** — Notifies immediately when a correct password is found
- 📶 **No Location Required** — Basic scanning works without Windows Location services

## Requirements

- Windows 10/11
- Python 3.7+ (for running from source)
- Administrator privileges (required for password testing via `netsh wlan`)

## Quick Start

### Option 1: Run the compiled EXE (easiest)
1. Download `WiFi Password Tester v4.exe` from the [Releases](../../releases) page
2. Right-click → **Run as administrator**
3. Click **Yes** on the UAC window
4. Click **🔄 Refresh Available WiFi List** to scan

### Option 2: Run from source
```cmd
cd WiFiPasswordTester_Clean
py main_v4.py
```

Or use the batch file:
```cmd
run.bat
```
*(Right-click `run.bat` → "Run as administrator" for full functionality)*

## How It Works

The app uses Windows built-in `netsh wlan` commands to:
1. Enumerate available networks (`netsh wlan show networks`)
2. Create temporary WiFi profiles with test passwords
3. Attempt connection to verify passwords
4. Clean up temporary profiles after testing

## Location Services

The launcher script (`Launch-WiFiApp.ps1`) automatically enables Windows Location Services before launching and disables them when you close the app. Basic scanning works without Location, but enabling it improves network detection.

## Security Notice

⚠️ **For authorized testing only** on networks you own or have explicit permission to test. Unauthorized access to WiFi networks is illegal in most jurisdictions.

Passwords are stored locally in `%USERPROFILE%\.wifi_password_db.json`. Keep this file secure.

## License

MIT License

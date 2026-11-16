# Launch-WiFiApp.ps1
# WiFi Password Tester v4 - Smart Launcher
# 1. Enables Windows Location services automatically
# 2. Launches the app as Administrator (UAC prompt - just click Yes)
# 3. Waits for you to close the app
# 4. Disables Location services automatically

$ErrorActionPreference = "Continue"

# === Paths (auto-detect folder where this script lives) ===
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$exePath = Join-Path $scriptDir "WiFi Password Tester v4.exe"

if (-not (Test-Path $exePath)) {
    # Fallback: look in dist folder
    $exePath = Join-Path $scriptDir "dist\WiFi Password Tester v4.exe"
}

if (-not (Test-Path $exePath)) {
    Write-Host "ERROR: Could not find 'WiFi Password Tester v4.exe'" -ForegroundColor Red
    Write-Host "Expected at: $exePath" -ForegroundColor Yellow
    pause
    exit 1
}

# === Step 1: Enable Windows Location Services ===
Write-Host "Enabling Location Services..." -ForegroundColor Cyan

try {
    # Enable location sensor (system-wide, may need admin but we try)
    $locKey = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Sensor\Overrides\{BFA794E4-F964-4FDB-90F6-5DF6E600466B}"
    if (-not (Test-Path $locKey)) { New-Item -Path $locKey -Force | Out-Null }
    Set-ItemProperty -Path $locKey -Name "SensorPermissionState" -Value 1 -Type DWord -ErrorAction SilentlyContinue

    # Enable location for current user (no admin needed)
    $userKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location"
    if (-not (Test-Path $userKey)) { New-Item -Path $userKey -Force | Out-Null }
    Set-ItemProperty -Path $userKey -Name "Value" -Value "Allow" -Type String -ErrorAction SilentlyContinue

    # Also enable for the location capability itself
    $capKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location"
    if (-not (Test-Path $capKey)) { New-Item -Path $capKey -Force | Out-Null }
    Set-ItemProperty -Path $capKey -Name "Value" -Value "Allow" -Type String -ErrorAction SilentlyContinue

    Write-Host "Location Services enabled." -ForegroundColor Green
} catch {
    Write-Host "Warning: Could not fully enable location (may need admin). The app will still work for basic scanning." -ForegroundColor Yellow
}

# === Step 2: Launch the app as Administrator (triggers UAC prompt) ===
Write-Host "Launching WiFi Password Tester v4 as Administrator..." -ForegroundColor Cyan
Write-Host "When the UAC window appears, click YES to continue." -ForegroundColor Yellow

try {
    $process = Start-Process -FilePath $exePath -Verb RunAs -Wait -PassThru
    Write-Host "App closed. Exit code: $($process.ExitCode)" -ForegroundColor Cyan
} catch {
    Write-Host "Failed to launch app: $_" -ForegroundColor Red
    pause
    exit 1
}

# === Step 3: Disable Location Services automatically on exit ===
Write-Host "Disabling Location Services..." -ForegroundColor Cyan

try {
    # Disable location sensor
    $locKey = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Sensor\Overrides\{BFA794E4-F964-4FDB-90F6-5DF6E600466B}"
    if (Test-Path $locKey) {
        Set-ItemProperty -Path $locKey -Name "SensorPermissionState" -Value 0 -Type DWord -ErrorAction SilentlyContinue
    }

    # Disable location for current user
    $userKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location"
    if (Test-Path $userKey) {
        Set-ItemProperty -Path $userKey -Name "Value" -Value "Deny" -Type String -ErrorAction SilentlyContinue
    }

    Write-Host "Location Services disabled." -ForegroundColor Green
} catch {
    Write-Host "Warning: Could not disable location automatically." -ForegroundColor Yellow
}

Write-Host "Done. You can close this window." -ForegroundColor Cyan

# Only pause if run directly (not from a shortcut)
if ($MyInvocation.InvocationName -ne ".") {
    pause
}

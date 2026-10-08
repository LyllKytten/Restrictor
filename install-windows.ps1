# Run in PowerShell as Administrator:
#   powershell -ExecutionPolicy Bypass -File install-windows.ps1
$ErrorActionPreference = "Stop"
$dir = "C:\ProgramData\HardBlocker"
if (Test-Path "$dir\blocker.py") {
    Write-Host "Already installed. To change settings: python $dir\blocker.py edit (applies after 24h)."
    Write-Host "To reinstall, run uninstall-windows.ps1 first (takes 15 minutes)."
    exit 1
}

$python = (Get-Command python).Source
& $python -m pip install psutil

New-Item -ItemType Directory -Force -Path $dir | Out-Null
Copy-Item "$PSScriptRoot\blocker.py", "$PSScriptRoot\config.json" $dir -Force

$pythonw = Join-Path (Split-Path $python) "pythonw.exe"
$settings = New-ScheduledTaskSettingsSet -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit ([TimeSpan]::Zero) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

$action = New-ScheduledTaskAction -Execute $pythonw -Argument "`"$dir\blocker.py`" run"
Register-ScheduledTask -TaskName "HardBlocker" -Action $action -Trigger (New-ScheduledTaskTrigger -AtStartup) `
    -Settings $settings -User "SYSTEM" -RunLevel Highest -Force | Out-Null

# Guard: every minute starts the blocker again if someone stopped it
$guardAction = New-ScheduledTaskAction -Execute "schtasks.exe" -Argument "/run /tn HardBlocker"
$guardTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName "HardBlockerGuard" -Action $guardAction -Trigger $guardTrigger `
    -Settings $settings -User "SYSTEM" -RunLevel Highest -Force | Out-Null

Start-ScheduledTask -TaskName "HardBlocker"
Write-Host "Installed. Check with: python $dir\blocker.py status"

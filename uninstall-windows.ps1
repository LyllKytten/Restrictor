# Run in PowerShell as Administrator. Takes 15 minutes on purpose.
$phrase = "I am giving up on my olympiad and my exams"
Write-Host "To remove the blocker, type exactly:"
Write-Host "  $phrase"
if ((Read-Host) -cne $phrase) { Write-Host "Wrong. Blocker stays."; exit 1 }

Write-Host "OK. Waiting 15 minutes. Close this window to cancel (good choice)."
for ($left = 15; $left -gt 0; $left--) { Write-Host "  $left minutes left..."; Start-Sleep -Seconds 60 }

Unregister-ScheduledTask -TaskName "HardBlockerGuard" -Confirm:$false -ErrorAction SilentlyContinue
Stop-ScheduledTask -TaskName "HardBlocker" -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName "HardBlocker" -Confirm:$false -ErrorAction SilentlyContinue
Get-Process pythonw -ErrorAction SilentlyContinue | Stop-Process -Force
python "C:\ProgramData\HardBlocker\blocker.py" clear
Remove-Item -Recurse -Force "C:\ProgramData\HardBlocker"
Write-Host "Removed."

# Setup Windows Task Scheduler for ARclinic SMM Agent
# Run this script as Administrator to create a monthly scheduled task.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File setup_scheduler.ps1
#
# This creates a task that runs at 09:00 on the 1st of every month.

$ErrorActionPreference = "Stop"

$TaskName = "ARclinic_SMM_Agent_Monthly"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonExe = (Get-Command python -ErrorAction SilentlyContinue).Source

if (-not $PythonExe) {
    $PythonExe = (Get-Command python3 -ErrorAction SilentlyContinue).Source
}
if (-not $PythonExe) {
    Write-Error "Python не найден. Установите Python 3 и добавьте в PATH."
    exit 1
}

Write-Host "Python: $PythonExe"
Write-Host "Script dir: $ScriptDir"

# Install dependencies
Write-Host "`n[1/3] Installing Python dependencies..."
Set-Location $ScriptDir
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Warning "Some dependencies may not have installed. Continuing..."
}

# Remove existing task if present
Write-Host "`n[2/3] Removing old task if exists..."
schtasks /Delete /TN $TaskName /F 2>$null

# Create scheduled task
Write-Host "`n[3/3] Creating scheduled task '$TaskName'..."
$Action = New-ScheduledTaskAction -Execute $PythonExe `
    -Argument "`"$ScriptDir\scheduler.py`"" `
    -WorkingDirectory $ScriptDir

$Trigger = New-ScheduledTaskTrigger -Monthly -DaysOfMonth 1 -At 09:00

$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 30) `
    -ExecutionTimeLimit (New-TimeSpan -Hours 2)

$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" `
    -LogonType Interactive `
    -RunLevel Highest

Register-ScheduledTask -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "ARclinic SMM Agent — ежемесячный парсинг соцсетей и отчёт на почту arclinic.adwords@gmail.com"

Write-Host "`n✅ Task '$TaskName' created successfully!"
Write-Host "   Runs: 1st of every month at 09:00"
Write-Host "   To run manually: schtasks /Run /TN '$TaskName'"
Write-Host "   To check status: schtasks /Query /TN '$TaskName' /V"
Write-Host "`n⚠️  Don't forget to configure SMTP_PASSWORD in .env file!"
Write-Host "   Gmail users: create App Password at https://myaccount.google.com/apppasswords"

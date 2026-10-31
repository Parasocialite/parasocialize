#requires -Version 5.1
<#
.SYNOPSIS
    Register (or preview) a Windows Scheduled Task that runs the daily build.

.WHY
    `tools/daily.py` is the loop, but a loop nobody starts is a document. The
    repository's GitHub workflow is the intended scheduler; it cannot run until
    the local history is pushed to a real remote. This is the local fallback for
    a machine that is on every day, and it is deliberately opt-in: it changes
    the machine's scheduler, which is not something a build script should do by
    itself.

.USAGE
    # see exactly what would be registered, change nothing
    powershell -ExecutionPolicy Bypass -File tools\install_daily_task.ps1

    # register it, every day at 08:20 local time
    powershell -ExecutionPolicy Bypass -File tools\install_daily_task.ps1 -Register

    # register and run once now
    powershell -ExecutionPolicy Bypass -File tools\install_daily_task.ps1 -Register -RunNow

    # remove it
    Unregister-ScheduledTask -TaskName ParasocializeDaily -Confirm:$false
#>
param(
    [switch]$Register,
    [switch]$RunNow,
    [string]$Time = "08:20",
    [string]$TaskName = "ParasocializeDaily"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$daily = Join-Path $root "tools\daily.py"
if (-not (Test-Path -LiteralPath $daily)) {
    throw "tools\daily.py not found at $daily - run this from the repository"
}

$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python) { throw "python is not on PATH" }

$action = New-ScheduledTaskAction -Execute $python `
    -Argument "-X utf8 `"$daily`"" -WorkingDirectory $root
$trigger = New-ScheduledTaskTrigger -Daily -At $Time
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable `
    -DontStopOnIdleEnd -ExecutionTimeLimit (New-TimeSpan -Hours 1)

Write-Host "task     $TaskName"
Write-Host "runs     $python -X utf8 `"$daily`""
Write-Host "workdir  $root"
Write-Host "daily at $Time (local); StartWhenAvailable catches a missed day"
Write-Host ""

if (-not $Register) {
    Write-Host "DRY RUN - nothing registered. Re-run with -Register to install."
    exit 0
}

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger `
    -Settings $settings -Description "Parasocialize daily build, record, gates and deploy package" `
    -Force | Out-Null
Write-Host "registered $TaskName"

if ($RunNow) {
    Start-ScheduledTask -TaskName $TaskName
    Write-Host "started; follow data/daily.json and the task history"
}

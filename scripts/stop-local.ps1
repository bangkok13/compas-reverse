$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pidFile = Join-Path $projectRoot '.runtime\local-processes.json'
if (-not (Test-Path -LiteralPath $pidFile)) { Write-Output 'No tracked local services.'; exit }
$entries = Get-Content -LiteralPath $pidFile -Raw | ConvertFrom-Json
function Stop-OwnedChildren([int]$parentId) {
    $children = Get-CimInstance Win32_Process -Filter "ParentProcessId = $parentId"
    foreach ($child in $children) {
        if ($child.CommandLine -and $child.CommandLine.Contains($projectRoot)) {
            Stop-OwnedChildren $child.ProcessId
            Stop-Process -Id $child.ProcessId -ErrorAction SilentlyContinue
        }
    }
}
foreach ($entry in $entries) {
    $running = Get-Process -Id $entry.Id -ErrorAction SilentlyContinue
    if ($running -and $running.StartTime.ToUniversalTime().ToString('o') -eq $entry.StartTime) {
        Stop-OwnedChildren $entry.Id
        Stop-Process -Id $entry.Id -ErrorAction SilentlyContinue
    }
}
Remove-Item -LiteralPath $pidFile
Write-Output 'Local services stopped.'

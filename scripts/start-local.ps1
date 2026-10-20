$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonPath = Join-Path $projectRoot '.venv\Scripts\python.exe'
$nodeCommand = Get-Command node -ErrorAction SilentlyContinue
if ($nodeCommand) {
    $nodePath = $nodeCommand.Source
} else {
    $portableNode = Get-ChildItem -LiteralPath (Join-Path $projectRoot '.tools') -Directory -Filter 'node-*-win-x64' -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $portableNode) { throw 'Install Node.js 22.22.3+ or use Docker Compose.' }
    $nodePath = Join-Path $portableNode.FullName 'node.exe'
}
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Create .venv and install backend/requirements/lock.txt first.' }
if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'frontend\.output\server\index.mjs'))) { throw 'Run npm run build in frontend first.' }
$occupied = Get-NetTCPConnection -State Listen -LocalPort 3000,8000 -ErrorAction SilentlyContinue
if ($occupied) { throw 'Port 3000 or 8000 is already in use. Stop the existing local instance first.' }
$runtimePath = Join-Path $projectRoot '.runtime'
New-Item -ItemType Directory -Force -Path $runtimePath | Out-Null
$pidFile = Join-Path $runtimePath 'local-processes.json'
if (Test-Path -LiteralPath $pidFile) {
    $previous = Get-Content -LiteralPath $pidFile -Raw | ConvertFrom-Json
    foreach ($entry in $previous) {
        $running = Get-Process -Id $entry.Id -ErrorAction SilentlyContinue
        if ($running -and $running.StartTime.ToUniversalTime().ToString('o') -eq $entry.StartTime) {
            throw 'Local services are already running. Use scripts/stop-local.ps1 first.'
        }
    }
}
$env:DEBUG = 'true'
$env:PYTHONIOENCODING = 'utf-8'
$env:DATABASE_URL = 'sqlite:///' + ((Join-Path $projectRoot 'backend\db.sqlite3') -replace '\\','/')
$env:NUXT_API_INTERNAL = 'http://127.0.0.1:8000/api'
$env:NUXT_PUBLIC_SITE_URL = 'http://127.0.0.1:3000'
$env:NUXT_PUBLIC_INDEXABLE = 'false'
$env:HOST = '127.0.0.1'
$env:PORT = '3000'
$env:SECURE_SSL_REDIRECT = 'false'
& $pythonPath (Join-Path $projectRoot 'backend\manage.py') migrate --noinput
if ($LASTEXITCODE -ne 0) { throw 'Migration failed.' }
& $pythonPath (Join-Path $projectRoot 'backend\manage.py') seed_demo
if ($LASTEXITCODE -ne 0) { throw 'Demo preparation failed.' }
$backend = Start-Process -FilePath $pythonPath -ArgumentList 'manage.py','runserver','127.0.0.1:8000','--noreload' -WorkingDirectory (Join-Path $projectRoot 'backend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtimePath 'backend.log') -RedirectStandardError (Join-Path $runtimePath 'backend-error.log')
$env:DEBUG = ''
$frontend = Start-Process -FilePath $nodePath -ArgumentList '.output/server/index.mjs' -WorkingDirectory (Join-Path $projectRoot 'frontend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtimePath 'frontend.log') -RedirectStandardError (Join-Path $runtimePath 'frontend-error.log')
@($backend, $frontend) | ForEach-Object { @{ Id = $_.Id; StartTime = $_.StartTime.ToUniversalTime().ToString('o') } } | ConvertTo-Json | Set-Content -LiteralPath $pidFile -Encoding UTF8
$ready = $false
for ($attempt = 0; $attempt -lt 30; $attempt++) {
    try {
        $response = Invoke-WebRequest 'http://127.0.0.1:3000/' -UseBasicParsing -TimeoutSec 3
        $apiResponse = Invoke-WebRequest 'http://127.0.0.1:8000/api/health/' -UseBasicParsing -TimeoutSec 3
        if ($response.StatusCode -eq 200 -and $apiResponse.StatusCode -eq 200) { $ready = $true; break }
    } catch { Start-Sleep -Milliseconds 500 }
}
if (-not $ready) {
    & (Join-Path $PSScriptRoot 'stop-local.ps1')
    throw 'Local startup failed. Inspect .runtime logs.'
}
Write-Output 'Site: http://127.0.0.1:3000 | Admin: http://127.0.0.1:8000/admin/'

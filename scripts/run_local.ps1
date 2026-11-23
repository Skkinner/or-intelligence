# Owner: Member D (WBS 7.1.1). One-command local run on Windows: API on :8000, web on :8080.
# Usage: powershell -ExecutionPolicy Bypass -File scripts\run_local.ps1
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

if (-not $env:INFERENCE_MODE) { $env:INFERENCE_MODE = "fixture" }
if (-not $env:STORAGE_DIR) { $env:STORAGE_DIR = "storage" }

# TODO(D, 7.1.1): create/activate .venv and install requirements\api.txt (+ ml.txt for real mode)
if ($env:INFERENCE_MODE -eq "real") { python -m src.inference.fetch_weights }

$api = Start-Process -PassThru -NoNewWindow python -ArgumentList "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"
try {
    Set-Location web
    if (-not (Test-Path node_modules)) { npm ci }
    $env:VITE_API_MOCK = "0"
    npm run build
    npm run preview -- --host 0.0.0.0
}
finally {
    if ($api -and -not $api.HasExited) { Stop-Process -Id $api.Id }
}

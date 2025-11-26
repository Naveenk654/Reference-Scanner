# Start Frontend Server
Write-Host "Starting Frontend Server..." -ForegroundColor Cyan
cd frontend
if (-not (Test-Path node_modules)) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}
npm run dev


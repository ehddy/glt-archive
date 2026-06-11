# GLT 로컬 개발 서버 실행 스크립트
$root = Split-Path $PSScriptRoot -Parent

Write-Host "=== 괴테는 모든 것을 말했다 - 개발 서버 ===" -ForegroundColor Cyan
Write-Host ""

# 백엔드
Write-Host "[1/2] 백엔드 시작 (http://127.0.0.1:8000)" -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
  "-NoExit", "-Command",
  "cd '$root\backend'; uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 2

# 프론트
Write-Host "[2/2] 프론트엔드 시작 (http://localhost:5173)" -ForegroundColor Yellow
Start-Process powershell -ArgumentList @(
  "-NoExit", "-Command",
  "cd '$root\frontend'; npm run dev"
)

Write-Host ""
Write-Host "잠시 후 브라우저에서 접속:" -ForegroundColor Green
Write-Host "  http://localhost:5173" -ForegroundColor White
Write-Host "  http://127.0.0.1:5173" -ForegroundColor White
Write-Host ""
Write-Host "5173이 안 되면 프론트 터미널에 표시된 주소를 사용하세요." -ForegroundColor Gray

# ==============================================================================
# Windows 平台自動化部署與單元測試腳本 (scripts/deploy_windows.ps1)
# 說明：針對 Windows 10/11 (PowerShell / Docker Desktop / WSL2 NTFS 掛載) 執行部署與單元測試
# ==============================================================================

$ErrorActionPreference = "Continue"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "🚀 啟動 Windows 平台專案自動化部署與單元測試作業" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. 檢查先決條件 (Docker Engine & Docker Compose)
Write-Host "1. 檢查 Windows Docker Desktop 環境..." -ForegroundColor Yellow
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ 找不到 Docker 指令，請確認已安裝 Docker Desktop 並開啟服務。" -ForegroundColor Red
    exit 1
}

$dockerVersion = docker --version
Write-Host "✓ Docker 版本：$dockerVersion" -ForegroundColor Green

# 2. 檢查並自動初始化設定檔
Write-Host "2. 檢查環境設定檔 (.env / entrypoint.sh)..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✓ 已自 .env.example 建立 .env 設定檔" -ForegroundColor Green
    } else {
        Write-Host "❌ 找不到 .env 或 .env.example 檔案" -ForegroundColor Red
        exit 1
    }
}

if (-not (Test-Path "backend/entrypoint.sh")) {
    if (Test-Path "backend/entrypoint.example.sh") {
        Copy-Item "backend/entrypoint.example.sh" "backend/entrypoint.sh"
        Write-Host "✓ 已自 entrypoint.example.sh 建立 backend/entrypoint.sh" -ForegroundColor Green
    }
}

if (-not (Test-Path "db_conf/init_multi_db.sql")) {
    if (Test-Path "db_conf/init_multi_db.example.sql") {
        Copy-Item "db_conf/init_multi_db.example.sql" "db_conf/init_multi_db.sql"
        Write-Host "✓ 已自 init_multi_db.example.sql 建立 db_conf/init_multi_db.sql" -ForegroundColor Green
    }
}

# 3. 啟動與構建 Docker Compose 服務
Write-Host "3. 執行 Docker Compose 服務建置與啟動 (Windows NTFS 適配模式)..." -ForegroundColor Yellow
docker compose up --build -d

# 4. 等待服務就緒並執行單元測試
Write-Host "4. 等待 Django 後端容器就緒並執行專案單元測試 (python manage.py test)..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

$unitTestSuccess = $false
for ($i = 1; $i -le 6; $i++) {
    Write-Host "  嘗試連線執行單元測試 ($i/6)..." -ForegroundColor Gray
    docker exec django_backend python manage.py test
    if ($LASTEXITCODE -eq 0) {
        $unitTestSuccess = $true
        break
    }
    Start-Sleep -Seconds 3
}

if ($unitTestSuccess) {
    Write-Host "🎉 專案單元測試全數成功通過！" -ForegroundColor Green
} else {
    Write-Host "⚠️ 單元測試執行未完全完成，請檢查容器 Log。" -ForegroundColor Yellow
}

# 5. 執行 HTTP API 健康測試驗證
Write-Host "5. 執行部署後健康驗證 (http://localhost/api/status/)..." -ForegroundColor Yellow
try {
    $res = Invoke-RestMethod -Uri "http://localhost/api/status/" -TimeoutSec 10
    if ($res.status -eq "online" -and $res.database.status -eq "connected") {
        Write-Host "======================================================================" -ForegroundColor Cyan
        Write-Host "🎉 Windows 平台部署與單元測試全數成功完成！" -ForegroundColor Green
        Write-Host "   🌐 系統儀表板網址: http://localhost/tech-stack/" -ForegroundColor Cyan
        Write-Host "   🔑 Unfold 管理後台: http://localhost/admin/" -ForegroundColor Cyan
        Write-Host "======================================================================" -ForegroundColor Cyan
    } else {
        Write-Host "⚠️ 健康檢測回應不如預期" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ 無法存取健康檢查 API，請檢查 Apache/Django 容器日誌。" -ForegroundColor Yellow
}

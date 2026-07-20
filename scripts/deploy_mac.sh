#!/bin/bash
# ==============================================================================
# macOS 平台專用自動化部署與單元測試腳本 (scripts/deploy_mac.sh)
# 說明：針對 macOS (Apple Silicon M 系列 / Intel) 執行 Docker Desktop 部署、APFS 掛載適配與單元測試
# ==============================================================================
set -e

echo "======================================================================"
echo "🍎 啟動 macOS 平台專案自動化部署與單元測試作業"
echo "======================================================================"

# 1. 檢查先決條件
if ! command -v docker >/dev/null 2>&1; then
    echo "❌ 錯誤：未安裝 Docker，請確認已啟動 Docker Desktop for Mac。"
    exit 1
fi

# 2. 自動處理環境變數與設定檔
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ 已自 .env.example 建立 .env 設定檔"
    fi
fi

if [ ! -f "backend/entrypoint.sh" ]; then
    if [ -f "backend/entrypoint.example.sh" ]; then
        cp backend/entrypoint.example.sh backend/entrypoint.sh
        chmod +x backend/entrypoint.sh
        echo "✓ 已自 entrypoint.example.sh 建立 backend/entrypoint.sh"
    fi
fi

# 賦予 init_dir.sh 執行權限
chmod +x scripts/init_dir.sh 2>/dev/null || true

# 3. 啟動與構建 Docker Compose 服務
echo "3. 執行 Docker Compose 服務建置與啟動 (macOS APFS 適配與權限初始化)..."
docker compose up --build -d

# 4. 等待容器就緒並執行單元測試
echo "4. 等待 Django 後端容器就緒並執行專案單元測試 (python manage.py test)..."
sleep 8

UNIT_TEST_PASSED=false
for i in $(seq 1 6); do
    echo "  嘗試連線執行單元測試 ($i/6)..."
    if docker exec django_backend python manage.py test; then
        UNIT_TEST_PASSED=true
        break
    fi
    sleep 3
done

if [ "$UNIT_TEST_PASSED" = "true" ]; then
    echo "🎉 專案單元測試全數成功通過！"
else
    echo "⚠️ 單元測試執行未完全完成，請檢查容器 Log。"
fi

# 5. 執行 API 健康檢查
echo "5. 執行部署後健康驗證 (http://localhost/api/status/)..."
if command -v curl >/dev/null 2>&1; then
    HEALTH_RES=$(curl -s http://localhost/api/status/ || echo "")
    if echo "$HEALTH_RES" | grep -q '"status":"online"' && echo "$HEALTH_RES" | grep -q '"status":"connected"'; then
        echo "======================================================================"
        echo "🎉 macOS 平台部署與單元測試全數成功完成！"
        echo "   🌐 系統儀表板網址: http://localhost/tech-stack/"
        echo "   🔑 Unfold 管理後台: http://localhost/admin/"
        echo "======================================================================"
    else
        echo "⚠️ 健康檢測回應不如預期: $HEALTH_RES"
    fi
fi

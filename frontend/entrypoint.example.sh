#!/bin/sh
# ==============================================================================
# Vue 3.5 前端開發服務容器啟動腳本 (frontend/entrypoint.sh)
# 說明：設定手動測試驗證環境 (SHOW_FRONTEND_VER) 資料夾與內容顯示/隱蔽，然後啟動 Vite。
# ==============================================================================
set -e

echo "======================================================================"
echo "🚀 啟動 Vue 前端容器啟動程序 (entrypoint.sh)"
echo "======================================================================"

# 設定手動測試驗證環境 (SHOW_FRONTEND_VER) 資料夾與內容顯示/隱蔽
echo "👉 設定前端手動測試驗證環境 (SHOW_FRONTEND_VER=${SHOW_FRONTEND_VER:-True})..."
if [ "${SHOW_FRONTEND_VER:-True}" = "True" ]; then
    echo "   👉 開發測試環境：建立 frontend_ver 軟連結以顯示資料夾與內容"
    if [ -d "/app/.frontend_ver" ]; then
        ln -sfn /app/.frontend_ver /app/frontend_ver
    fi
else
    echo "   🔒 正式上線環境：隱蔽 frontend_ver 資料夾與內容"
    if [ -L "/app/frontend_ver" ]; then
        rm -f /app/frontend_ver
    elif [ -d "/app/frontend_ver" ]; then
        if [ ! -d "/app/.frontend_ver" ]; then
            mv /app/frontend_ver /app/.frontend_ver
        else
            rm -rf /app/frontend_ver
        fi
    fi
fi

# 啟動前端開發伺服器
echo "👉 啟動前端開發伺服器 (npm run dev)..."
exec npm run dev

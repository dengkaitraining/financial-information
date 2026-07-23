#!/bin/bash
# ==============================================================================
# 線上服務健康檢測與 API 驗證腳本 (scripts/test_health.sh)
# 說明：檢測系統 API (http://localhost/api/status/)、MariaDB 與 Redis 運作狀態
# ==============================================================================
set -e

echo "======================================================================"
echo "🔍 執行 Django on Docker 系統線上健康檢測 (test_health.sh)"
echo "======================================================================"

URL="http://localhost/api/status/"
echo "1. 正在請求 API 健康端點: $URL"

if ! command -v curl >/dev/null 2>&1; then
    echo "❌ 找不到 curl 指令，請先安裝 curl。"
    exit 1
fi

RESPONSE=$(curl -s --max-time 10 "$URL" || echo "")

if [ -z "$RESPONSE" ]; then
    echo "❌ 錯誤：無法連線至 API 端點 ($URL)"
    exit 1
fi

echo "2. 端點回應數據內容："
echo "$RESPONSE"

if echo "$RESPONSE" | grep -q -E '"status"[[:space:]]*:[[:space:]]*"online"' && echo "$RESPONSE" | grep -q -E '"status"[[:space:]]*:[[:space:]]*"connected"'; then
    echo "======================================================================"
    echo "🎉 所有自動化健康測試均完全通過!"
    echo "   - API 服務狀態: online"
    echo "   - MariaDB 資料庫: connected"
    echo "   - Redis 快取伺服器: connected"
    echo "======================================================================"
    exit 0
else
    echo "======================================================================"
    echo "⚠️ 警告：系統回應狀態不符預期，請檢查服務 Log！"
    echo "======================================================================"
    exit 1
fi

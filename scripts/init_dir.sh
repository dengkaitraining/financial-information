#!/bin/sh
# ==============================================================================
# 自動初始化目錄與權限修復腳本 (scripts/init_dir.sh)
# 說明：自動判斷宿主機作業系統 (Windows / Linux / macOS)，並根據不同 OS 執行目錄建立與權限修復作業
# ==============================================================================
set -e

echo "======================================================================"
echo "📁 啟動自動初始化目錄與權限修復服務 (init-dir)"
echo "======================================================================"

# 1. 自動檢測宿主機作業系統 (Host OS Auto-Detection)
# 可透過 .env 內的 HOST_OS 強制覆寫 (windows, linux, mac)，否則自動根據系統核心特徵判斷
HOST_OS_TYPE="${HOST_OS:-auto}"
if [ "$HOST_OS_TYPE" = "auto" ]; then
    if grep -qi "microsoft\|wsl" /proc/version 2>/dev/null; then
        HOST_OS_TYPE="windows"
    elif grep -qi "linuxkit" /proc/version 2>/dev/null; then
        HOST_OS_TYPE="mac"
    else
        HOST_OS_TYPE="linux"
    fi
fi

# 2. 定義需要初始化的資料與設定目錄
#TARGET_DIRS="/app/db_data /app/redis_data /app/backend /app/frontend /app/apache /app/db_conf /app/redis_conf"
TARGET_DIRS="/app/db_data /app/redis_data"

echo "1. 檢查並建立所需之資料與設定實體目錄..."
for dir in $TARGET_DIRS; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "   + 建立目錄: $dir"
    else
        echo "   ✓ 目錄已存在: $dir"
    fi
done

# 3. 根據宿主機作業系統 (Host OS) 執行專屬權限修復邏輯
echo "2. 執行宿主機 OS 專屬權限修復作業 ($HOST_OS_TYPE 模式)..."

case "$HOST_OS_TYPE" in
    windows)
        echo "💻 檢測到宿主機作業系統：Windows (WSL2 / Docker Desktop)"
        echo "   👉 執行 Windows NTFS / WSL2 實體目錄權限適配修復..."
        # Windows (NTFS / WSL2 掛載模式):
        # WSL2 / Windows 檔案系統會映射 NTFS 權限。將 db_data 與 redis_data 設為 777 可避開 MariaDB / Redis 容器寫入與權限拒絕的問題
        chmod -R 777 /app/db_data /app/redis_data 2>/dev/null || true
        echo "   ✓ Windows NTFS 權限修復完成 (chmod 777)"
        ;;
    mac)
        echo "🍎 檢測到宿主機作業系統：macOS (Docker Desktop / APFS)"
        echo "   👉 執行 macOS APFS / Docker Desktop 權限適配修復..."
        # macOS (APFS / VirtioFS / gRPC FUSE):
        # macOS 掛載點由 Docker Desktop 虛擬化核心處理，設定開放權限並維護存取點
        chmod -R 777 /app/db_data /app/redis_data 2>/dev/null || true
        echo "   ✓ macOS APFS 權限修復完成 (chmod 777)"
        ;;
    linux|*)
        echo "🐧 檢測到宿主機作業系統：Native Linux (Ubuntu / Debian / RHEL)"
        echo "   👉 執行 Linux 原生 UID/GID 與讀寫權限修復..."
        # Native Linux:
        # 確保 MariaDB (UID 999) 與 Redis (UID 999) 或根使用者容器皆具備讀寫實體目錄權限
        chmod -R 777 /app/db_data /app/redis_data 2>/dev/null || true
        if command -v chown >/dev/null 2>&1; then
            chown -R 999:999 /app/db_data /app/redis_data 2>/dev/null || chmod -R 777 /app/db_data /app/redis_data 2>/dev/null || true
        fi
        echo "   ✓ Native Linux 權限修復完成"
        ;;
esac

echo "======================================================================"
echo "🎉 初始化目錄與權限修復服務 (init-dir) 執行完畢！"
echo "======================================================================"

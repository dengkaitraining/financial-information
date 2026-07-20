#!/bin/bash
# ==============================================================================
# 跨平台統一自動化部署與單元測試進入點腳本 (scripts/deploy.sh)
# 說明：自動檢測目前宿主機作業系統 (Linux / macOS / Windows WSL / Git Bash)，並派發至專屬部署腳本
# ==============================================================================
set -e

echo "======================================================================"
echo "🚀 啟動 Django on Docker 跨平台統一自動化部署進入點 (deploy.sh)"
echo "======================================================================"

# 偵測 Host OS
HOST_OS_TYPE="linux"
UNAME_STR=$(uname -s 2>/dev/null || echo "Unknown")

case "$UNAME_STR" in
    Darwin*)
        HOST_OS_TYPE="mac"
        ;;
    Linux*)
        if grep -qi "microsoft\|wsl" /proc/version 2>/dev/null; then
            HOST_OS_TYPE="windows"
        else
            HOST_OS_TYPE="linux"
        fi
        ;;
    MINGW*|MSYS*|CYGWIN*)
        HOST_OS_TYPE="windows"
        ;;
    *)
        HOST_OS_TYPE="linux"
        ;;
esac

case "$HOST_OS_TYPE" in
    mac)
        echo "🍎 判斷為 macOS 環境，轉接至 ./scripts/deploy_mac.sh..."
        chmod +x ./scripts/deploy_mac.sh 2>/dev/null || true
        exec ./scripts/deploy_mac.sh "$@"
        ;;
    windows)
        echo "💻 判斷為 Windows (WSL / Git Bash) 環境..."
        if command -v powershell.exe >/dev/null 2>&1; then
            echo "👉 執行 Windows PowerShell 部署腳本 (deploy_windows.ps1)..."
            powershell.exe -ExecutionPolicy Bypass -File ./scripts/deploy_windows.ps1
        else
            echo "👉 轉接至 Linux/WSL 相容部署腳本 (deploy_linux.sh)..."
            chmod +x ./scripts/deploy_linux.sh 2>/dev/null || true
            exec ./scripts/deploy_linux.sh "$@"
        fi
        ;;
    linux|*)
        echo "🐧 判斷為 Native Linux 環境，轉接至 ./scripts/deploy_linux.sh..."
        chmod +x ./scripts/deploy_linux.sh 2>/dev/null || true
        exec ./scripts/deploy_linux.sh "$@"
        ;;
esac

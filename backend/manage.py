#!/usr/bin/env python
"""
Django 專案管理命令列入口腳本 (manage.py)
說明：提供專案運作、資料庫遷移、建立超級使用者與開發伺服器啟動之命令介面
"""
import os
import sys

def main():
    """執行 Django 命令行管理工作"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "無法匯入 Django 套件。請確認已成功安裝 Django 並且位於正確的 Python 環境中。"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()

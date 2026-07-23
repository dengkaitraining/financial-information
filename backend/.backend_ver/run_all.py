#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
後端環境手動測試驗證整合執行器 (run_all.py)
說明：一鍵執行所有後端手動測試（Django 環境、MariaDB 多資料庫、Redis 快取），並顯示最終整合報告。
"""
import os
import sys

# 確保可以 import backend_ver 底下的模組
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_ver.test_django_env import test_django_environment
from backend_ver.test_db_conn import test_db_connections
from backend_ver.test_redis_conn import test_redis_connection

def main():
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    django.setup()
    from django.conf import settings

    if not getattr(settings, 'SHOW_BACKEND_VER', True):
        print("=" * 80)
        print("🔒 [安全防護] 正式上線模式已啟用。")
        print("👉 已依據控制參數 SHOW_BACKEND_VER=False 隱蔽手動測試驗證資料 (backend_ver)。")
        print("=" * 80)
        sys.exit(0)

    print("=" * 80)
    print("🚀 啟動 fin_django_backend 後端手動測試整合驗證程序")
    print("=" * 80)

    try:
        # 1. 執行 Django 系統與環境檢查
        test_django_environment()
        print("\n")

        # 2. 執行 MariaDB 雙資料庫連線檢查
        test_db_connections()
        print("\n")

        # 3. 執行 Redis 8.8 快取與連線檢查
        test_redis_connection()
        print("\n")

        print("=" * 80)
        print("🎉 所有手動測試驗證已順利完成！請檢閱上方詳細輸出以確認各服務狀態。")
        print("=" * 80)

    except Exception as e:
        print("\n🔴 執行手動測試驗證程序時發生未預期錯誤:")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

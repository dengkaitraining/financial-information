#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Redis 快取與 Session 伺服器手動測試驗證腳本 (test_redis_conn.py)
說明：此腳本用於手動驗證 Redis 快取連線以及資料存取功能。
"""
import os
import sys
import django
import time

# 設定 Django 環境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from django.core.cache import cache

def test_redis_connection():
    if not getattr(settings, 'SHOW_BACKEND_VER', True):
        print("🔒 [安全防護] 正式上線環境已隱蔽手動測試驗證資料。")
        return

    print("=" * 60)
    print("🔍 啟動 Redis 8.8 快取與連線驗證...")
    print("=" * 60)

    try:
        # 1. 測試連線資訊
        from django_redis import get_redis_connection
        con = get_redis_connection("default")
        info = con.info()
        print("🟢 Redis 伺服器連線成功！")
        print(f"  👉 Redis 版本: {info.get('redis_version')}")
        print(f"  👉 記憶體使用量: {info.get('used_memory_human')}")
        print(f"  👉 連線客戶端數: {info.get('connected_clients')}")
        
        # 2. 測試快取寫入與讀取 (Set & Get)
        print("\n[步驟 1] 測試 Django Cache API (Set/Get)")
        test_key = "backend_ver_test_key"
        test_val = f"hello_redis_at_{int(time.time())}"
        
        print(f"  👉 寫入快取: key='{test_key}', value='{test_val}'")
        cache.set(test_key, test_val, timeout=10)
        
        retrieved_val = cache.get(test_key)
        print(f"  👉 讀取快取: key='{test_key}', value='{retrieved_val}'")
        
        if retrieved_val == test_val:
            print("🟢 快取資料比對成功！")
        else:
            print("🔴 快取資料比對失敗！讀取到的數值不相符。")
            
        # 3. 測試快取刪除 (Delete)
        print("\n[步驟 2] 測試 Django Cache API (Delete)")
        cache.delete(test_key)
        deleted_val = cache.get(test_key)
        print(f"  👉 刪除後讀取: key='{test_key}', value={deleted_val}")
        if deleted_val is None:
            print("🟢 快取資料刪除成功！")
        else:
            print("🔴 快取資料刪除失敗！資料仍殘留。")

    except Exception as e:
        print(f"🔴 Redis 連線或操作失敗: {e}")

    print("\n" + "=" * 60)
    print("✨ Redis 8.8 連線驗證完成。")
    print("=" * 60)

if __name__ == '__main__':
    test_redis_connection()

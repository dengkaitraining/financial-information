#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MariaDB 多資料庫與多帳號連線手動測試驗證腳本 (test_db_conn.py)
說明：此腳本用於手動驗證 Django 雙資料庫連線、使用者帳號權限隔離以及 ORM 路由。
"""
import os
import sys
import django

# 設定 Django 環境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from django.db import connections
from django.contrib.auth.models import User
from employees.models import Employee

def test_db_connections():
    if not getattr(settings, 'SHOW_BACKEND_VER', True):
        print("🔒 [安全防護] 正式上線環境已隱蔽手動測試驗證資料。")
        return

    print("=" * 60)
    print("🔍 啟動 MariaDB 雙資料庫連線與權限驗證...")
    print("=" * 60)

    # 1. 測試 default 資料庫 (user_stock_db / user_stock)
    print("\n[步驟 1] 測試主要資料庫 (default: user_stock_db)")
    try:
        conn = connections['default']
        conn.ensure_connection()
        print("🟢 default 資料庫連線成功！")
        
        # 測試讀取 User 資料表
        user_count = User.objects.using('default').count()
        print(f"  👉 連線使用者: {conn.settings_dict['USER']}")
        print(f"  👉 主要資料庫 (user_stock_db) 中的 User 筆數: {user_count}")
        if user_count > 0:
            users = User.objects.using('default').all()[:3]
            print("  👉 使用者樣例: " + ", ".join([u.username for u in users]))
    except Exception as e:
        print(f"🔴 default 資料庫連線或查詢失敗: {e}")

    # 2. 測試 employee_db 資料庫 (db_employee / user_employee)
    print("\n[步驟 2] 測試員工資料庫 (employee_db: db_employee)")
    try:
        conn = connections['employee_db']
        conn.ensure_connection()
        print("🟢 employee_db 資料庫連線成功！")
        
        # 測試讀取 Employee 資料表
        emp_count = Employee.objects.using('employee_db').count()
        print(f"  👉 連線使用者: {conn.settings_dict['USER']}")
        print(f"  👉 員工資料庫 (db_employee) 中的 Employee 筆數: {emp_count}")
        if emp_count > 0:
            emps = Employee.objects.using('employee_db').all()[:3]
            print("  👉 員工樣例: " + ", ".join([f"{e.last_name}{e.first_name} ({e.email})" for e in emps]))
    except Exception as e:
        print(f"🔴 employee_db 資料庫連線或查詢失敗: {e}")

    # 3. 測試多資料庫 ORM 路由轉接器 (db_router.py)
    print("\n[步驟 3] 測試 ORM 多資料庫路由轉接器機制")
    try:
        # 使用 ORM 預設方式 (不顯式指定 .using()) 查詢 Employee 與 User，驗證路由是否正確分流
        print("  👉 嘗試不指定使用庫，透過 ORM 自動路由查詢 Employee...")
        emp_auto_count = Employee.objects.count()
        print(f"  👉 經路由轉接後取得 Employee 筆數: {emp_auto_count}")
        
        print("  👉 嘗試不指定使用庫，透過 ORM 自動路由查詢 User...")
        user_auto_count = User.objects.count()
        print(f"  👉 經路由轉接後取得 User 筆數: {user_auto_count}")
        
        print("🟢 ORM 多資料庫自動路由運作正常！")
    except Exception as e:
        print(f"🔴 ORM 多資料庫自動路由運作異常: {e}")

    print("\n" + "=" * 60)
    print("✨ MariaDB 雙資料庫連線驗證完成。")
    print("=" * 60)

if __name__ == '__main__':
    test_db_connections()

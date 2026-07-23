#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Django 5.2 系統環境與設定手動測試驗證腳本 (test_django_env.py)
說明：此腳本用於檢查 Django 的環境變數設定與系統檢查 (System Check)。
"""
import os
import sys
import django

# 設定 Django 環境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from django.conf import settings

def test_django_environment():
    if not getattr(settings, 'SHOW_BACKEND_VER', True):
        print("🔒 [安全防護] 正式上線環境已隱蔽手動測試驗證資料。")
        return

    print("=" * 60)
    print("🔍 啟動 Django 5.2 系統環境與設定驗證...")
    print("=" * 60)

    # 1. 輸出系統與版本資訊
    print("\n[步驟 1] 系統與版本資訊:")
    print(f"  👉 Python 版本: {sys.version.split()[0]}")
    print(f"  👉 Django 版本: {django.get_version()}")
    print(f"  👉 專案 BASE_DIR: {settings.BASE_DIR}")
    print(f"  👉 DEBUG 模式: {settings.DEBUG}")

    # 2. 檢查環境變數
    print("\n[步驟 2] 重要環境變數設定:")
    env_vars = [
        'HOST_OS', 'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER',
        'EMPLOYEE_DB_USER', 'EMPLOYEE_DB_NAME', 'REDIS_HOST',
        'REDIS_PORT', 'DJANGO_ALLOWED_HOSTS'
    ]
    for var in env_vars:
        val = os.environ.get(var, '(未設定 / 預設值)')
        print(f"  👉 {var}: {val}")

    # 3. 執行 Django 系統自我檢查 (System Check)
    print("\n[步驟 3] 執行 Django 內建系統自我檢查 (System Check)...")
    try:
        # call_command('check') 會執行 Django 所有的檢查器
        call_command('check', stdout=sys.stdout, stderr=sys.stderr)
        print("🟢 Django 系統自我檢查通過，無嚴重錯誤！")
    except Exception as e:
        print(f"🔴 Django 系統自我檢查失敗: {e}")

    print("\n" + "=" * 60)
    print("✨ Django 5.2 系統環境驗證完成。")
    print("=" * 60)

if __name__ == '__main__':
    test_django_environment()

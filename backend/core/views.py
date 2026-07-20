"""
Django 視圖處理函式 (core/views.py)
說明：提供根目錄 (/) 簡單文字回應與 MariaDB/Redis 連線動態檢測 API (/api/status/)
"""
from django.http import HttpResponse, JsonResponse
from django.db import connection
from django.core.cache import cache
import sys

def home_view(request):
    """
    根目錄 (/) 視圖處理函式
    回傳簡單文字資訊："Django + Vue.js Web 資訊系統開發環境的服務已啟用。"
    """
    return HttpResponse(
        "Django + Vue.js Web 資訊系統開發環境的服務已啟用。",
        content_type="text/plain; charset=utf-8"
    )

def health_check(request):
    """
    健康檢查 API 視圖函式 (/api/status/)
    動態檢測 MariaDB 與 Redis 連線狀態，傳回系統資訊 JSON 格式
    """
    db_status = "unknown"
    db_error = None
    try:
        # 實作數據庫連線查詢檢測
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = "error"
        db_error = str(e)

    redis_status = "unknown"
    redis_error = None
    try:
        # 測試 Redis 寫入與讀取能力
        cache.set("health_check_key", "working", timeout=10)
        val = cache.get("health_check_key")
        if val == "working":
            redis_status = "connected"
        else:
            redis_status = "error"
            redis_error = "Redis 寫入成功但讀取值不一致"
    except Exception as e:
        redis_status = "error"
        redis_error = str(e)

    return JsonResponse({
        "status": "online",
        "django_version": "5.2 LTS",
        "python_version": sys.version,
        "database": {
            "status": db_status,
            "error": db_error,
            "engine": connection.settings_dict.get('ENGINE'),
            "host": connection.settings_dict.get('HOST'),
            "name": connection.settings_dict.get('NAME'),
        },
        "redis": {
            "status": redis_status,
            "error": redis_error,
        }
    })

# ==============================================================================
# Django Core Package 初始化 (backend/core/__init__.py)
# 說明：確保 Django 啟動時載入 celery_app，使 @shared_task 註解正常運作
# ==============================================================================

from .celery import app as celery_app

__all__ = ('celery_app',)

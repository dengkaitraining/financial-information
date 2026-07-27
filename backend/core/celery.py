# ==============================================================================
# Celery 任務非同步/排程設定檔 (backend/core/celery.py)
# 說明：初始化 Celery app，綁定 Django 專案 settings 設定
# ==============================================================================

import os
from celery import Celery

# 設定 Django settings 作為 Celery 的設定來源
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# 使用 'CELERY_' 作為 settings 裡所有 Celery 配置的鍵名前綴
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自動發現各個 Django App (如 core, employees) 底下的 tasks.py 任務
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

"""
ASGI 異步伺服器網關介面配置 (core/asgi.py)
說明：供異步 Web 伺服器 (如 Daphne / Uvicorn) 或 WebSocket / Channels 處理呼叫
"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_asgi_application()

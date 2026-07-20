"""
WSGI Web 伺服器網關介面配置 (core/wsgi.py)
說明：供同步網网页伺服器 (如 Apache mod_wsgi / Gunicorn) 呼叫之進入點
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()

# ==============================================================================
# Django 核心路由設定檔 (backend/core/urls.py)
# 說明：對接根目錄 (/)、Unfold 後台 (/admin/) 與動態健康檢查 API (/api/status/)
# ==============================================================================

from django.contrib import admin
from django.urls import path
from .views import home_view, health_check

urlpatterns = [
    # 根目錄 (/)：回應純文字訊息
    path('', home_view, name='home'),

    # Django Unfold 後台管理介面 (/admin/)
    path('admin/', admin.site.urls),

    # 動態健康檢測 API (/api/status/)
    path('api/status/', health_check, name='health_check'),
]

# ==============================================================================
# Django 核心路由設定檔 (backend/core/urls.py)
# 說明：配置健康檢查、Unfold 後台、股票查詢與 More 詳情頁面路由
# ==============================================================================

from django.contrib import admin
from django.urls import path
from .views import (
    home_view, 
    health_check, 
    stock_fetch_api, 
    stock_calendar_view, 
    stock_news_view
)

urlpatterns = [
    # 根目錄 (/)：回應純文字訊息
    path('', home_view, name='home'),

    # Django Unfold 後台管理介面 (/admin/)
    path('admin/', admin.site.urls),

    # 動態健康檢測 API (/api/status/)
    path('api/status/', health_check, name='health_check'),

    # 股票查詢與即時更新 API (/api/stock/fetch/)
    path('api/stock/fetch/', stock_fetch_api, name='stock_fetch_api'),

    # 更多行事曆分頁 (/stock/calendar/<stock_id>/)
    path('stock/calendar/<str:stock_id>/', stock_calendar_view, name='stock_calendar_view'),

    # 更多新聞與公告分頁 (/stock/news/<stock_id>/)
    path('stock/news/<str:stock_id>/', stock_news_view, name='stock_news_view'),
]

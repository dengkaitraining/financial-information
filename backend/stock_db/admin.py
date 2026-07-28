# ==============================================================================
# 股票模組 Django Unfold Admin 設定檔 (backend/stock_db/admin.py)
# 說明：配置台股公司資料、行事曆、新聞、技術分析與排程清單的 Unfold 後台管理
# ==============================================================================

from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import CompanyProfile, CompanyCalendar, CompanyNews, StockScheduleList, TechnicalAnalysis

@admin.register(CompanyProfile)
class CompanyProfileAdmin(ModelAdmin):
    list_display = [
        'stock_id', 'company_name', 'chairman', 'general_manager',
        'market_type', 'industry_category', 'market_cap_millions',
        'capital', 'updated_at'
    ]
    list_filter = ['market_type', 'industry_category']
    search_fields = ['stock_id', 'company_name', 'chairman', 'general_manager', 'industry_category']
    ordering = ['stock_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CompanyCalendar)
class CompanyCalendarAdmin(ModelAdmin):
    list_display = ['stock', 'event_type', 'event_date', 'description', 'updated_at']
    list_filter = ['event_type', 'event_date']
    search_fields = ['stock__stock_id', 'stock__company_name', 'description']
    ordering = ['-event_date']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CompanyNews)
class CompanyNewsAdmin(ModelAdmin):
    list_display = ['stock', 'news_type', 'title', 'publisher', 'published_date', 'updated_at']
    list_filter = ['news_type', 'publisher', 'published_date']
    search_fields = ['stock__stock_id', 'stock__company_name', 'title', 'summary']
    ordering = ['-published_date']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(StockScheduleList)
class StockScheduleListAdmin(ModelAdmin):
    list_display = ['stock_id', 'analysis_period', 'created_at', 'updated_at']
    search_fields = ['stock_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TechnicalAnalysis)
class TechnicalAnalysisAdmin(ModelAdmin):
    list_display = ['stock', 'trade_date', 'volume', 'close_price', 'k_value', 'd_value', 'macd', 'bias', 'updated_at']
    list_filter = ['trade_date', 'stock__stock_id']
    search_fields = ['stock__stock_id', 'stock__company_name', 'trade_date']
    ordering = ['-trade_date']
    readonly_fields = ['created_at', 'updated_at']

# ==============================================================================
# 核心模組 Django Unfold Admin 設定檔 (backend/core/admin.py)
# 說明：配置台股公司資料、行事曆、新聞、排程清單與 Django Celery Beat 介面
# ==============================================================================

from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import CompanyProfile, CompanyCalendar, CompanyNews, StockScheduleList

# 重新註冊 django-celery-beat 模型至 Unfold
from django_celery_beat.admin import PeriodicTaskAdmin, CrontabScheduleAdmin
from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule, SolarSchedule, ClockedSchedule

admin.site.unregister(PeriodicTask)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(SolarSchedule)
admin.site.unregister(ClockedSchedule)

@admin.register(PeriodicTask)
class UnfoldPeriodicTaskAdmin(PeriodicTaskAdmin, ModelAdmin):
    pass

@admin.register(CrontabSchedule)
class UnfoldCrontabScheduleAdmin(CrontabScheduleAdmin, ModelAdmin):
    pass

@admin.register(IntervalSchedule)
class UnfoldIntervalScheduleAdmin(ModelAdmin):
    pass

@admin.register(SolarSchedule)
class UnfoldSolarScheduleAdmin(ModelAdmin):
    pass

@admin.register(ClockedSchedule)
class UnfoldClockedScheduleAdmin(ModelAdmin):
    pass


# 註冊我們自定義的台股資料表
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
    list_display = ['stock_id', 'created_at', 'updated_at']
    search_fields = ['stock_id']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

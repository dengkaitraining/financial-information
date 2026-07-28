# ==============================================================================
# 核心模組 Django Unfold Admin 設定檔 (backend/core/admin.py)
# 說明：配置 Django Celery Beat 介面
# ==============================================================================

from django.contrib import admin
from unfold.admin import ModelAdmin

# 重新註冊 django-celery-beat 模型至 Unfold
from django_celery_beat.admin import PeriodicTaskAdmin, CrontabScheduleAdmin
from django_celery_beat.models import PeriodicTask, CrontabSchedule, IntervalSchedule, SolarSchedule, ClockedSchedule

try:
    admin.site.unregister(PeriodicTask)
    admin.site.unregister(CrontabSchedule)
    admin.site.unregister(IntervalSchedule)
    admin.site.unregister(SolarSchedule)
    admin.site.unregister(ClockedSchedule)
except Exception:
    pass

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

# ==============================================================================
# 員工管理 Django Unfold Admin 設定檔 (backend/employees/admin.py)
# 說明：配置 Django Unfold 介面展示與管理員工主資料表 (employees)
# ==============================================================================

from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Employee

@admin.register(Employee)
class EmployeeAdmin(ModelAdmin):
    """
    Django Unfold ModelAdmin: 員工主資料表管理介面
    """
    list_display = [
        'employee_num', 'last_name', 'first_name', 'gender',
        'status', 'hire_date', 'email', 'phone', 'manager'
    ]
    list_filter = ['status', 'gender', 'hire_date']
    search_fields = ['employee_num', 'first_name', 'last_name', 'national_id', 'email', 'phone']
    ordering = ['-id']
    fieldsets = (
        ('基本身份資訊', {
            'fields': ('employee_num', 'last_name', 'first_name', 'national_id', 'gender', 'birth_date')
        }),
        ('聯絡資訊', {
            'fields': ('email', 'personal_email', 'phone')
        }),
        ('組織與職務', {
            'fields': ('department_id', 'job_title_id', 'manager', 'status', 'hire_date', 'termination_date')
        }),
    )

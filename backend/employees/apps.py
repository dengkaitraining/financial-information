# ==============================================================================
# Django 員工管理模組 App 組態 (backend/employees/apps.py)
# 說明：定義 EmployeesConfig，對應 db_employee 資料庫之員工主資料表 (employees)
# ==============================================================================

from django.apps import AppConfig

class EmployeesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'employees'
    verbose_name = '員工管理系統'

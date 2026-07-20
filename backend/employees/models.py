# ==============================================================================
# 員工主資料表 Django Model (backend/employees/models.py)
# 說明：定義員工主資料表 (employees)，對應 db_employee 資料庫
# ==============================================================================

from django.db import models

class Employee(models.Model):
    """
    員工主資料表 (employees)
    """
    class Gender(models.IntegerChoices):
        UNKNOWN = 0, '未知'
        MALE = 1, '男'
        FEMALE = 2, '女'
        NON_BINARY = 3, '非二元'

    class Status(models.IntegerChoices):
        RESIGNED = 0, '離職'
        ACTIVE = 1, '在職'
        UNPAID_LEAVE = 2, '留職停薪'
        PROBATION = 3, '試用期'

    id = models.BigAutoField(primary_key=True, help_text='內部關聯使用的代理鍵 (Surrogate Key)')
    employee_num = models.CharField(max_length=20, unique=True, verbose_name='員工工號', help_text='例如：EMP2026001')
    first_name = models.CharField(max_length=50, verbose_name='名字', help_text='區分姓與名有利於國際化系統設計')
    last_name = models.CharField(max_length=50, verbose_name='姓氏', help_text='區分姓與名有利於國際化系統設計')
    national_id = models.CharField(max_length=20, unique=True, verbose_name='身分證字號 / 護照號碼', help_text='機敏資料')
    gender = models.PositiveSmallIntegerField(choices=Gender.choices, default=Gender.UNKNOWN, verbose_name='性別', help_text='0: 未知, 1: 男, 2: 女, 3: 非二元')
    birth_date = models.DateField(verbose_name='出生日期', help_text='計算員工法定年齡與生日福利')
    email = models.EmailField(max_length=100, unique=True, verbose_name='公司電子信箱', help_text='用於系統登入與公務通知')
    personal_email = models.EmailField(max_length=100, null=True, blank=True, verbose_name='個人電子信箱', help_text='離職聯絡或緊急狀況備用')
    phone = models.CharField(max_length=20, verbose_name='行動電話', help_text='純數字存放')
    department_id = models.IntegerField(null=True, blank=True, verbose_name='所屬部門 ID', help_text='關聯至部門表 (departments.id)')
    job_title_id = models.IntegerField(null=True, blank=True, verbose_name='職務 / 職稱 ID', help_text='關聯至職稱表 (job_titles.id)')
    manager = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subordinates', db_column='manager_id', verbose_name='直屬主管 ID', help_text='自我關聯建立組織樹')
    status = models.PositiveSmallIntegerField(choices=Status.choices, default=Status.ACTIVE, verbose_name='員工狀態', help_text='0: 離職, 1: 在職, 2: 留職停薪, 3: 試用期')
    hire_date = models.DateField(verbose_name='到職日期', help_text='計算年資與特休假特權的基準')
    termination_date = models.DateField(null=True, blank=True, verbose_name='離職日期', help_text='員工離職時填入，在職時為 NULL')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='資料建立時間')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='資料更新時間')

    class Meta:
        db_table = 'employees'
        verbose_name = '員工主資料表'
        verbose_name_plural = '員工主資料表'
        ordering = ['-id']

    def __str__(self):
        return f"{self.employee_num} - {self.last_name}{self.first_name}"

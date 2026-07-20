# ==============================================================================
# 員工資料隨機種子建立腳本 (backend/employees/management/commands/seed_employees.py)
# 說明：自動在 db_employee 資料庫之 employees 資料表中生成 10 筆隨機測試員工資料
# ==============================================================================

import random
from datetime import date
from django.core.management.base import BaseCommand
from employees.models import Employee

class Command(BaseCommand):
    help = '自動產生 10 筆測試員工主資料 (db_employee)'

    def handle(self, *args, **options):
        if Employee.objects.using('employee_db').count() >= 10:
            self.stdout.write(self.style.SUCCESS('employees 資料庫已存在 10 筆以上員工資料，跳過自動產生。'))
            return

        sample_employees = [
            {"num": "EMP2026001", "first": "大明", "last": "陳", "nid": "A123456789", "gender": 1, "birth": date(1985, 5, 20), "email": "daming.chen@company.com", "phone": "0912345678", "hire": date(2020, 3, 1), "dept": 101, "job": 10, "status": 1},
            {"num": "EMP2026002", "first": "美麗", "last": "林", "nid": "B223456780", "gender": 2, "birth": date(1990, 8, 15), "email": "meili.lin@company.com", "phone": "0923456789", "hire": date(2021, 6, 15), "dept": 101, "job": 11, "status": 1},
            {"num": "EMP2026003", "first": "志豪", "last": "張", "nid": "C123456781", "gender": 1, "birth": date(1988, 11, 3), "email": "zhihao.chang@company.com", "phone": "0934567890", "hire": date(2019, 1, 10), "dept": 102, "job": 20, "status": 1},
            {"num": "EMP2026004", "first": "淑芬", "last": "黃", "nid": "D223456782", "gender": 2, "birth": date(1992, 2, 28), "email": "shufen.huang@company.com", "phone": "0945678901", "hire": date(2022, 9, 1), "dept": 102, "job": 21, "status": 1},
            {"num": "EMP2026005", "first": "冠宇", "last": "李", "nid": "E123456783", "gender": 1, "birth": date(1995, 7, 7), "email": "guanyu.lee@company.com", "phone": "0956789012", "hire": date(2023, 4, 12), "dept": 103, "job": 30, "status": 1},
            {"num": "EMP2026006", "first": "佩君", "last": "趙", "nid": "F223456784", "gender": 2, "birth": date(1993, 12, 19), "email": "peijun.zhao@company.com", "phone": "0967890123", "hire": date(2023, 8, 1), "dept": 103, "job": 31, "status": 3},
            {"num": "EMP2026007", "first": "家豪", "last": "許", "nid": "G123456785", "gender": 1, "birth": date(1987, 4, 30), "email": "jiahao.hsu@company.com", "phone": "0978901234", "hire": date(2018, 5, 20), "dept": 104, "job": 40, "status": 1},
            {"num": "EMP2026008", "first": "怡婷", "last": "郭", "nid": "H223456786", "gender": 2, "birth": date(1996, 10, 10), "email": "yiting.guo@company.com", "phone": "0989012345", "hire": date(2024, 1, 15), "dept": 104, "job": 41, "status": 3},
            {"num": "EMP2026009", "first": "文彬", "last": "曾", "nid": "I123456787", "gender": 3, "birth": date(1991, 3, 25), "email": "wenbin.tseng@company.com", "phone": "0990123456", "hire": date(2022, 11, 1), "dept": 101, "job": 12, "status": 2},
            {"num": "EMP2026010", "first": "家瑋", "last": "鄭", "nid": "J123456788", "gender": 1, "birth": date(1984, 9, 5), "email": "jiawei.cheng@company.com", "phone": "0901234567", "hire": date(2017, 7, 1), "dept": 101, "job": 1, "status": 1},
        ]

        created_objs = []
        for emp_data in sample_employees:
            obj, created = Employee.objects.using('employee_db').get_or_create(
                employee_num=emp_data["num"],
                defaults={
                    "first_name": emp_data["first"],
                    "last_name": emp_data["last"],
                    "national_id": emp_data["nid"],
                    "gender": emp_data["gender"],
                    "birth_date": emp_data["birth"],
                    "email": emp_data["email"],
                    "personal_email": f"personal_{emp_data['num'].lower()}@gmail.com",
                    "phone": emp_data["phone"],
                    "department_id": emp_data["dept"],
                    "job_title_id": emp_data["job"],
                    "status": emp_data["status"],
                    "hire_date": emp_data["hire"]
                }
            )
            created_objs.append(obj)

        # 設定主管關聯 (組織樹)
        if len(created_objs) >= 3:
            manager_top = created_objs[-1] # 鄭家瑋
            for emp in created_objs[:4]:
                emp.manager = manager_top
                emp.save(using='employee_db')

        self.stdout.write(self.style.SUCCESS('成功新增 10 筆測試員工資料至 db_employee (employees 資料表)！'))

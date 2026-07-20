# ==============================================================================
# 員工模組單元測試 (backend/employees/tests.py)
# 說明：測試 Employee Model、欄位校驗、CRUD 操作與 seed_employees Management Command
# ==============================================================================

from django.test import TestCase
from django.core.management import call_command
from django.utils import timezone
from employees.models import Employee

class EmployeeModelTestCase(TestCase):
    """
    測試 Employee Model 的 CRUD 與資料庫操作 (使用 employee_db 資料庫)
    databases = {'default', 'employee_db'}
    """
    databases = {'default', 'employee_db'}

    def setUp(self):
        self.employee = Employee.objects.using('employee_db').create(
            employee_num='EMP999001',
            first_name='測試',
            last_name='張',
            national_id='A123456789',
            gender=Employee.Gender.MALE,
            birth_date=timezone.now().date(),
            email='test.chang@example.com',
            phone='0912345678',
            status=Employee.Status.ACTIVE,
            hire_date=timezone.now().date(),
        )

    def test_employee_creation(self):
        """測試員工資料新增與存取"""
        emp = Employee.objects.using('employee_db').get(employee_num='EMP999001')
        self.assertEqual(emp.first_name, '測試')
        self.assertEqual(emp.last_name, '張')
        self.assertEqual(emp.gender, Employee.Gender.MALE)
        self.assertEqual(emp.status, Employee.Status.ACTIVE)
        self.assertEqual(str(emp), 'EMP999001 - 張測試')

    def test_employee_update(self):
        """測試員工資料更新"""
        self.employee.status = Employee.Status.PROBATION
        self.employee.save(using='employee_db')

        updated_emp = Employee.objects.using('employee_db').get(employee_num='EMP999001')
        self.assertEqual(updated_emp.status, Employee.Status.PROBATION)

    def test_employee_deletion(self):
        """測試員工資料刪除"""
        emp_id = self.employee.id
        self.employee.delete(using='employee_db')
        self.assertFalse(Employee.objects.using('employee_db').filter(id=emp_id).exists())


class SeedEmployeesCommandTestCase(TestCase):
    """
    測試 seed_employees 自動產生 10 筆測試員工主資料管理指令
    """
    databases = {'default', 'employee_db'}

    def test_seed_employees_command(self):
        """測試執行 seed_employees 指令並驗證生成的 10 筆員工資料"""
        # 執行種子產生指令
        call_command('seed_employees')

        # 驗證數據庫中是否包含資料
        count = Employee.objects.using('employee_db').count()
        self.assertGreaterEqual(count, 10)

# ==============================================================================
# Django 核心模組單元測試 (backend/core/tests.py)
# 說明：測試根目錄回應、/api/status/ 健康檢查 JSON API、多資料庫路由與 Redis 快取
# ==============================================================================

from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from core.db_router import PrimaryEmployeeRouter
from employees.models import Employee

class CoreViewsTestCase(TestCase):
    """
    測試核心視圖 (Views) 與端點回應
    """
    def setUp(self):
        self.client = Client()

    def test_home_view(self):
        """測試根目錄 (/) 回應狀態碼與文字內容"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn("Django + Vue.js Web 資訊系統開發環境的服務已啟用。", response.content.decode('utf-8'))

    def test_health_check_api(self):
        """測試 /api/status/ 健康檢查 API JSON 格式與結構"""
        response = self.client.get('/api/status/')
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data.get('status'), 'online')
        self.assertEqual(data.get('django_version'), '5.2 LTS')
        self.assertIn('database', data)
        self.assertIn('redis', data)
        self.assertEqual(data['database'].get('status'), 'connected')
        self.assertEqual(data['redis'].get('status'), 'connected')


class DatabaseRouterTestCase(TestCase):
    """
    測試 PrimaryEmployeeRouter 多資料庫路由轉接器
    """
    def setUp(self):
        self.router = PrimaryEmployeeRouter()

    def test_db_for_read_and_write(self):
        """測試 Employee 模型讀寫是否導向 employee_db"""
        self.assertEqual(self.router.db_for_read(Employee), 'employee_db')
        self.assertEqual(self.router.db_for_write(Employee), 'employee_db')

    def test_allow_migrate(self):
        """測試 Migration 導向權限"""
        # employees 模組僅允許在 employee_db 進行 migration
        self.assertTrue(self.router.allow_migrate('employee_db', 'employees'))
        self.assertFalse(self.router.allow_migrate('default', 'employees'))

        # 其他模組僅允許在 default 進行 migration
        self.assertTrue(self.router.allow_migrate('default', 'auth'))
        self.assertFalse(self.router.allow_migrate('employee_db', 'auth'))


class RedisCacheTestCase(TestCase):
    """
    測試 Redis 快取連線與讀寫功能
    """
    def test_cache_set_and_get(self):
        """測試 Redis 快取寫入與取得能力"""
        cache_key = "unit_test_key"
        cache_val = "unit_test_value_2026"

        cache.set(cache_key, cache_val, timeout=60)
        retrieved_val = cache.get(cache_key)
        self.assertEqual(retrieved_val, cache_val)

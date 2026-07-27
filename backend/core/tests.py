# ==============================================================================
# Django 核心模組單元測試 (backend/core/tests.py)
# 說明：測試根目錄回應、/api/status/ 健康檢查 JSON API、多資料庫路由與 Redis 快取
# ==============================================================================

from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from core.db_router import PrimaryEmployeeRouter
from employees.models import Employee
from unittest import mock
from core.models import CompanyProfile, CompanyCalendar, CompanyNews, StockScheduleList

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


class StockFeatureTestCase(TestCase):
    """
    測試台股公司資料、行事曆、新聞公告之 ORM、API 與 Template 渲染
    """
    def setUp(self):
        self.client = Client()
        # 建立測試資料 (由於有外鍵約束，需依序建立)
        self.profile = CompanyProfile.objects.create(
            stock_id="2330",
            company_name="台積電",
            chairman="魏哲家",
            general_manager="魏哲家",
            market_type="上市",
            industry_category="半導體業",
            capital=259300000000.00
        )
        self.calendar = CompanyCalendar.objects.create(
            stock=self.profile,
            event_type="股東常會",
            event_date="2026-06-08",
            description="常會開會"
        )
        self.news = CompanyNews.objects.create(
            stock=self.profile,
            news_type="NEWS",
            title="台積電新聞標題",
            url="https://example.com/news/1",
            publisher="中央社",
            published_date="2026-07-27 12:00:00"
        )

    def test_orm_creation(self):
        """測試 Model 建立與關聯"""
        self.assertEqual(CompanyProfile.objects.count(), 1)
        self.assertEqual(CompanyCalendar.objects.count(), 1)
        self.assertEqual(CompanyNews.objects.count(), 1)
        
        # 測試外鍵與反向查詢
        self.assertEqual(self.profile.calendars.first().event_type, "股東常會")
        self.assertEqual(self.profile.news.first().title, "台積電新聞標題")

    def test_stock_fetch_api_local(self):
        """測試從本機查詢已有的股票資料 API"""
        response = self.client.get('/api/stock/fetch/', {'stock_id': '2330', 'update': 'false'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertTrue(data.get('has_data'))
        self.assertEqual(data['profile'].get('company_name'), '台積電')
        self.assertEqual(len(data.get('calendar', [])), 1)
        self.assertEqual(len(data.get('news', [])), 1)

    def test_stock_fetch_api_not_found(self):
        """測試本機查詢未存在的股票資料"""
        response = self.client.get('/api/stock/fetch/', {'stock_id': '9999', 'update': 'false'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertFalse(data.get('has_data'))

    @mock.patch('core.views.StockProfileFetcher')
    def test_stock_fetch_api_update(self, mock_fetcher_cls):
        """測試即時更新爬蟲與儲存 API (Mock 外部抓取)"""
        # 設定 mock instance 的回傳值
        mock_fetcher = mock_fetcher_cls.return_value
        mock_fetcher.fetch_profile.return_value = {
            'stock_id': '2330',
            'company_name': '台積電',
            'chairman': '魏哲家',
            'general_manager': '魏哲家',
            'market_type': '上市',
            'industry_category': '半導體業'
        }
        mock_fetcher.fetch_calendar.return_value = [
            {'stock_id': '2330', 'event_type': '現金股利發放日', 'event_date': '2026-09-15', 'description': '除權息'}
        ]
        mock_fetcher.fetch_news_and_announcements.return_value = (
            [{'stock_id': '2330', 'news_type': 'NEWS', 'title': '台積電新新聞', 'url': 'http://link1', 'publisher': 'GNews', 'published_date': '2026-07-27 13:00:00', 'summary': '摘要'}],
            []
        )

        response = self.client.get('/api/stock/fetch/', {'stock_id': '2330', 'update': 'true'})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))
        self.assertTrue(data.get('has_data'))
        
        # 驗證資料是否已經寫入資料庫且有排程清單
        self.assertTrue(StockScheduleList.objects.filter(stock_id='2330').exists())

    def test_detail_views(self):
        """測試行事曆與新聞的 More 詳情頁面渲染"""
        # 行事曆詳情
        response = self.client.get('/stock/calendar/2330/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "台積電")
        self.assertContains(response, "股東常會")

        # 新聞詳情
        response = self.client.get('/stock/news/2330/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "台積電")
        self.assertContains(response, "台積電新聞標題")


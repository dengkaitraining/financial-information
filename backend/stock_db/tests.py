# ==============================================================================
# 股票模組單元測試 (backend/stock_db/tests.py)
# 說明：測試股票 Models、技術分析資料寫入與 Scraper 指標計算
# ==============================================================================

from django.test import TestCase
from stock_db.models import CompanyProfile, CompanyCalendar, CompanyNews, StockScheduleList, TechnicalAnalysis
from stock_db.scraper.db_django import DjangoDatabaseManager
from stock_db.scraper.ta_analyzer import TAAnalyzer
import datetime
import pandas as pd

class StockDBTestCase(TestCase):
    def setUp(self):
        # 1. 建立測試公司基本資料
        self.profile = CompanyProfile.objects.create(
            stock_id="2330",
            company_name="台積電",
            chairman="魏哲家",
            general_manager="魏哲家",
            listing_date=datetime.date(1994, 9, 5),
            market_type="上市",
            industry_category="半導體業"
        )

        # 2. 建立測試排程更新股票 (預設 analysis_period 應為 3)
        self.schedule = StockScheduleList.objects.create(
            stock_id="2330"
        )

    def test_models_creation(self):
        """測試 Models 是否能成功建立與讀取"""
        self.assertEqual(CompanyProfile.objects.count(), 1)
        self.assertEqual(StockScheduleList.objects.count(), 1)
        
        # 驗證排程清單預設區間為 3 年
        self.assertEqual(self.schedule.analysis_period, 3)

    def test_technical_analysis_foreign_key(self):
        """測試 TechnicalAnalysis 外鍵與寫入約束"""
        ta = TechnicalAnalysis.objects.create(
            stock=self.profile,
            trade_date=datetime.date(2026, 7, 28),
            volume=15000000,
            close_price=950.00,
            k_value=50.25,
            d_value=48.50,
            j_value=53.75,
            macd=1.234,
            macd_signal=1.123
        )
        self.assertEqual(TechnicalAnalysis.objects.count(), 1)
        self.assertEqual(ta.stock.stock_id, "2330")

    def test_upsert_technical_analysis(self):
        """測試 DjangoDatabaseManager 批量技術分析資料寫入與更新 (upsert)"""
        db_manager = DjangoDatabaseManager()
        
        # 建立 Mock Pandas DataFrame
        df_data = {
            'Date': [datetime.date(2026, 7, 27), datetime.date(2026, 7, 28)],
            'Volume': [12000000, 15000000],
            'Open': [945.0, 948.0],
            'High': [955.0, 958.0],
            'Low': [940.0, 944.0],
            'Close': [950.0, 952.0],
            'K': [45.0, 50.25],
            'D': [42.0, 48.50],
            'J': [51.0, 53.75],
            'MACD': [1.0, 1.234],
            'MACD_Signal': [0.9, 1.123],
            'BIAS': [1.5, 1.8],
            'Williams_R': [-30.0, -25.0],
            'BBI': [942.5, 946.0],
            'CDP': [946.0, 951.0],
            'AH': [960.0, 965.0],
            'NH': [952.0, 957.0],
            'NL': [938.0, 943.0],
            'AL': [930.0, 935.0],
            'PDI': [25.0, 28.0],
            'MDI': [22.0, 20.0],
            'ADX': [30.0, 32.0]
        }
        df = pd.DataFrame(df_data)
        
        # 測試首次 bulk_create 寫入
        written = db_manager.upsert_technical_analysis("2330", df)
        self.assertEqual(written, 2)
        self.assertEqual(TechnicalAnalysis.objects.count(), 2)

        # 測試第二次重複主鍵時之 upsert 更新
        df.loc[1, 'Close'] = 960.00  # 修改收盤價
        written_again = db_manager.upsert_technical_analysis("2330", df)
        # bulk_create 會覆寫更新
        updated_ta = TechnicalAnalysis.objects.get(stock=self.profile, trade_date=datetime.date(2026, 7, 28))
        self.assertEqual(float(updated_ta.close_price), 960.00)

    def test_ta_analyzer_get_yf_stock_id(self):
        """測試 yfinance 股票代號格式解析"""
        analyzer = TAAnalyzer()
        # 測試台積電 (2330)
        self.assertEqual(analyzer.get_yf_stock_id("2330"), "2330.TW")
        # 測試隨意代號
        self.assertEqual(analyzer.get_yf_stock_id("9999"), "9999.TWO")

    def test_news_url_text_field_and_long_url(self):
        """測試 CompanyNews.url 欄位改為 Text 後，支援大於 500/1000 字元的超長連結寫入且不截斷"""
        db_manager = DjangoDatabaseManager()
        
        # 產生一個長達 1000 字元的超長 URL
        long_url = "https://example.com/news/" + ("a" * 900) + "/index.html"
        self.assertTrue(len(long_url) > 900)
        
        news_data = [{
            'stock_id': '2330',
            'news_type': 'NEWS',
            'title': '台積電長網址新聞測試',
            'url': long_url,
            'publisher': 'Yahoo Finance',
            'published_date': datetime.datetime.now(),
            'summary': '測試超長 url 儲存。'
        }]
        
        # 執行 upsert
        written = db_manager.upsert_news(news_data)
        self.assertEqual(written, 1)
        self.assertEqual(CompanyNews.objects.count(), 1)
        
        # 從資料庫中讀出並驗證長度與內容
        saved_news = CompanyNews.objects.get(stock=self.profile)
        self.assertEqual(saved_news.url, long_url)
        self.assertEqual(len(saved_news.url), len(long_url))


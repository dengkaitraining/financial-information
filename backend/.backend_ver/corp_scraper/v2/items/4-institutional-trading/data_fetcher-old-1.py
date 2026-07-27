import yfinance as yf
import twstock
import pandas as pd
from googletrans import Translator
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import random
import time

class StockDataFetcher:
    def __init__(self):
        self.translator = Translator()

    def get_start_date(self, period):
        now = datetime.now()
        """
        if period == '1M': return now - relativedelta(months=1)
        elif period == '1Q': return now - relativedelta(months=3)
        elif period == '6M': return now - relativedelta(months=6)
        elif period == '1Y': return now - relativedelta(years=1)
        """
        if period == '1Y': return now - relativedelta(years=1)
        elif period == '2Y': return now - relativedelta(years=2)
        elif period == '3Y': return now - relativedelta(years=3)
        elif period == '4Y': return now - relativedelta(years=4)
        return now - relativedelta(months=1)

    def _generate_dates(self, start_date):
        """產生工作日清單供模擬資料使用"""
        dates = []
        current_date = start_date
        while current_date <= datetime.now().date():
            if current_date.weekday() < 5: # 排除週末
                dates.append(current_date)
            current_date += timedelta(days=1)
        return dates

    def fetch_yfinance_institutional(self, stock_id, period):
        """1. 抓取 YFinance 機構持股並翻譯"""
        print(f"正在從 yfinance 抓取 {stock_id} 籌碼資料...")
        ticker = yf.Ticker(f"{stock_id}.TW")
        inst_holders = ticker.institutional_holders
        
        if inst_holders is None or inst_holders.empty:
            return []

        start_date = self.get_start_date(period).date()
        records = []

        for _, row in inst_holders.iterrows():
            date_reported = row.get('Date Reported')
            if isinstance(date_reported, pd.Timestamp):
                date_reported = date_reported.date()
            if date_reported < start_date:
                continue

            holder_en = row.get('Holder', '')
            shares = row.get('Shares', 0)
            out_ratio = row.get('% Out', 0.0)
            value = row.get('Value', 0)

            holder_zh = holder_en
            if holder_en:
                try:
                    translation = self.translator.translate(holder_en, src='en', dest='zh-tw')
                    holder_zh = translation.text
                except Exception as e:
                    print(f"翻譯失敗 [{holder_en}]: {e}")

            records.append((stock_id, date_reported, holder_en, holder_zh, shares, out_ratio, value))
        return records
    # (2026-07-27) fetch_daily_trading_margin --- { start } ----
    def fetch_daily_trading_margin(self, stock_id, period):
        """2. 抓取法人逐日買賣超 & 資券餘額 (模擬資料)"""
        print(f"正在抓取 {stock_id} 法人逐日買賣超與資券餘額...")
        start_date = self.get_start_date(period).date()
        dates = self._generate_dates(start_date)
        records = []
        
        # 實務上應使用 requests 解析 TWSE 或證交所 API
        for trade_date in dates:
            # 模擬產生欄位: (外資, 投信, 自營, 合計, 外資%, 漲跌幅, 成交量, 融資, 融券, 借券)
            records.append((
                stock_id, trade_date,
                random.randint(-5000, 5000), random.randint(-1000, 1000), random.randint(-500, 500), random.randint(-6500, 6500),
                round(random.uniform(20.0, 40.0), 2), round(random.uniform(-5.0, 5.0), 2), random.randint(10000, 50000),
                random.randint(5000, 15000), random.randint(500, 2000), random.randint(1000, 5000)
            ))
        return records
    # (2026-07-27) fetch_daily_trading_margin --- { end } ----

    def fetch_major_players(self, stock_id, period):
        """3. 抓取主力進出 (券商分點) (模擬資料)"""
        print(f"正在抓取 {stock_id} 主力進出(券商分點)...")
        start_date = self.get_start_date(period).date()
        dates = self._generate_dates(start_date)
        records = []
        brokers = ['凱基-台北', '元大-館前', '富邦', '群益']
        
        for trade_date in dates[-5:]: # 模擬只取最近5天
            for broker in brokers:
                is_buy = random.choice([True, False])
                trade_type = 'BUY' if is_buy else 'SELL'
                buy_v = random.randint(500, 2000) if is_buy else random.randint(0, 500)
                sell_v = random.randint(0, 500) if is_buy else random.randint(500, 2000)
                net_v = buy_v - sell_v
                records.append((stock_id, trade_date, broker, trade_type, buy_v, sell_v, net_v))
        return records

    def fetch_large_shareholders(self, stock_id, period):
        """4. 抓取大戶籌碼與董監持股 (模擬資料)"""
        print(f"正在抓取 {stock_id} 大戶籌碼...")
        start_date = self.get_start_date(period).date()
        dates = self._generate_dates(start_date)
        records = []
        
        # 模擬每週五公佈一次集保戶股權
        for trade_date in dates:
            if trade_date.weekday() == 4: # Friday
                records.append((
                    stock_id, trade_date,
                    round(random.uniform(20.0, 40.0), 2), round(random.uniform(50.0, 70.0), 2), 
                    round(random.uniform(10.0, 20.0), 2), round(random.uniform(100.0, 600.0), 2)
                ))
        return records
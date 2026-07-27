import yfinance as yf
import twstock
from googletrans import Translator
import pandas as pd
from datetime import datetime, timedelta

class StockFetcher:
    def __init__(self):
        self.translator = Translator()

    def get_stock_info(self, stock_id):
        try:
            stock = twstock.Stock(stock_id)
            return True, f"成功找到股票: {stock_id}"
        except Exception as e:
            return False, f"股票 {stock_id} 資訊獲取失敗"

    """
    def translate_keys(self, keys):
        # 批量翻譯英文財報科目為繁體中文以供顯示確認
        translations = self.translator.translate(keys, src='en', dest='zh-TW')
        return {item.origin: item.text for item in translations}
    """
    def translate_keys(self, keys):
        # 1. 建立常用財報科目的靜態字典，避免 googletrans 報錯並提升執行速度
        financial_dict = {
            "Total Revenue": "營業收入",
            "Gross Profit": "營業毛利",
            "Operating Expense": "營業費用",
            "Operating Income": "營業利益",
            "Net Income": "稅後淨利",
            "Total Assets": "總資產",
            "Total Liabilities Net Minority Interest": "總負債",
            "Stockholders Equity": "股東權益",
            "Current Assets": "流動資產",
            "Current Liabilities": "流動負債",
            "Operating Cash Flow": "營業現金流",
            "Investing Cash Flow": "投資現金流",
            "Financing Cash Flow": "融資現金流",
            "Free Cash Flow": "自由現金流",
            "Basic EPS": "每股盈餘"
        }
        
        result = {}
        for key in keys:
            # 優先查表
            if key in financial_dict:
                result[key] = financial_dict[key]
            else:
                # 2. 如果字典沒有，再嘗試使用 googletrans 單筆翻譯
                try:
                    translation = self.translator.translate(key, src='en', dest='zh-TW')
                    result[key] = translation.text
                except Exception as e:
                    print(f"[警告] '{key}' 翻譯失敗，將保留原文。({e})")
                    result[key] = key # 翻譯失敗則保留原始英文
                    
        return result

    def fetch_financials(self, stock_id, period="1y"):
        """
        period 可傳入 yfinance 支援格式，因 yfinance 財報預設回傳最近四季，
        我們在過濾時依據給定的時間範圍 (1mo, 3mo, 6mo, 1y) 篩選 date。
        """
        yf_ticker = f"{stock_id}.TW"
        ticker = yf.Ticker(yf_ticker)
        
        # 取得季報
        income = ticker.quarterly_financials
        balance = ticker.quarterly_balance_sheet
        cashflow = ticker.quarterly_cashflow
        
        # 計算時間範圍
        cutoff_date = datetime.now()
        if period == "1mo": cutoff_date -= timedelta(days=30)
        elif period == "1q": cutoff_date -= timedelta(days=90)
        elif period == "6mo": cutoff_date -= timedelta(days=180)
        else: cutoff_date -= timedelta(days=365) # 1y
        #else: cutoff_date -= timedelta(days=3650) # 10y

        results = {
            "income": [],
            "balance": [],
            "cashflow": [],
            "monthly_revenue": [], # 預留給額外爬取證交所月營收使用
            "quarterly_eps": []    # 從 income statement 萃取
        }

        # 處理損益表
        if not income.empty:
            # 為了計算 QoQ, YoY，這裡會需要進行額外的數值處理 (實務上通常需抓取更長期的資料來計算增長率)
            # 以下示範基本 EPS 寫入，增長率與均價欄位先以 None 替代，待有歷史資料時再計算
            for date in income.columns:
                if date >= pd.Timestamp(cutoff_date):
                    date_str = date.strftime('%Y-%m-%d')

                    # 1. 寫入損益表
                    results["income"].append((
                        #stock_id, date.strftime('%Y-%m-%d'),
                        stock_id, date_str,
                        self._safe_get(income, date, "Total Revenue"),
                        self._safe_get(income, date, "Gross Profit"),
                        self._safe_get(income, date, "Operating Expense"),
                        self._safe_get(income, date, "Operating Income"),
                        self._safe_get(income, date, "Net Income")
                    ))

                    # 2. 寫入單季 EPS (從損益表中取得 Basic EPS 或 Diluted EPS)
                    eps_val = self._safe_get(income, date, "Basic EPS")
                    if eps_val is not None:
                        results["quarterly_eps"].append((
                            stock_id, date_str,
                            float(eps_val),
                            None, # QoQ (需寫迴圈計算相鄰季度的變化)
                            None, # YoY (需歷史資料對比去年同期)
                            None  # 季均價 (需額外調用 twstock 歷史股價計算)
                        ))
                    
        # 處理資產負債表
        if not balance.empty:
            for date in balance.columns:
                if date >= pd.Timestamp(cutoff_date):
                    results["balance"].append((
                        stock_id, date.strftime('%Y-%m-%d'),
                        self._safe_get(balance, date, "Total Assets"),
                        self._safe_get(balance, date, "Total Liabilities Net Minority Interest"), # yfinance key
                        self._safe_get(balance, date, "Stockholders Equity"),
                        self._safe_get(balance, date, "Current Assets"),
                        self._safe_get(balance, date, "Current Liabilities")
                    ))

        # 處理現金流量表
        if not cashflow.empty:
            for date in cashflow.columns:
                if date >= pd.Timestamp(cutoff_date):
                    results["cashflow"].append((
                        stock_id, date.strftime('%Y-%m-%d'),
                        self._safe_get(cashflow, date, "Operating Cash Flow"),
                        self._safe_get(cashflow, date, "Investing Cash Flow"),
                        self._safe_get(cashflow, date, "Financing Cash Flow"),
                        self._safe_get(cashflow, date, "Free Cash Flow"),
                        self._safe_get(cashflow, date, "Net Income") # 近似淨現金流變動
                    ))

        return results

    def _safe_get(self, df, col, key):
        if key in df.index:
            val = df.at[key, col]
            return None if pd.isna(val) else int(val)
        return None
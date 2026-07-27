import yfinance as yf
import twstock
from googletrans import Translator
import pandas as pd
from datetime import datetime, timedelta
import requests
from io import StringIO

class StockFetcher:
    def __init__(self):
        self.translator = Translator()

    def get_stock_info(self, stock_id):
        try:
            stock = twstock.Stock(stock_id)
            return True, f"成功找到股票: {stock_id}"
        except Exception as e:
            return False, f"股票 {stock_id} 資訊獲取失敗"

    def translate_keys(self, keys):
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
            if key in financial_dict:
                result[key] = financial_dict[key]
            else:
                try:
                    translation = self.translator.translate(key, src='en', dest='zh-TW')
                    result[key] = translation.text
                except Exception as e:
                    result[key] = key 
        return result

    def _clean_number(self, val):
        """清洗財報字串數字，轉為浮點數或整數"""
        if pd.isna(val) or val == '-' or val == '': 
            return None
        if isinstance(val, str):
            val = val.replace(',', '').strip()
            try:
                return float(val) if '.' in val else int(val)
            except ValueError:
                return None
        return val

    def _fetch_mops_monthly_revenue(self, stock_id, period):
        """從公開資訊觀測站(MOPS)抓取月營收 - 採用全年彙總表(t146sb05)"""
        import time
        months_to_fetch = {"1mo": 1, "1q": 3, "6mo": 6, "1y": 12}.get(period, 12)
        
        # 決定需要抓取的民國年份 (為確保跨年資料，多抓前一年)
        current_year = datetime.now().year
        target_years = [current_year, current_year - 1]
        
        results = []
        
        for y in target_years:
            roc_year = y - 1911 # 轉換為民國年
            # 改用 t146sb05，給年份就會回傳該年1~12月所有已有資料
            url = "https://mops.twse.com.tw/mops/web/ajax_t146sb05"
            payload = {
                "encodeURIComponent": "1",
                "step": "1",
                "firstin": "1",
                "off": "1",
                "co_id": stock_id,
                "year": str(roc_year)
            }
            # 加入完整的 Header，避免被 MOPS 伺服器阻擋 (403 Forbidden)
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
                "Referer": "https://mops.twse.com.tw/mops/web/t146sb05"
            }
            
            try:
                res = requests.post(url, data=payload, headers=headers, timeout=10)
                res.encoding = 'utf-8'
                time.sleep(1) # 禮貌性延遲，避免連續 Request 被鎖 IP
                
                if "<table" not in res.text:
                    continue
                    
                # 讀取 HTML 表格
                dfs = pd.read_html(StringIO(res.text))
                df = None
                
                # 尋找目標表格，並攤平多層次欄位 (MultiIndex)
                for temp_df in dfs:
                    if isinstance(temp_df.columns, pd.MultiIndex):
                        temp_df.columns = ['_'.join(str(c) for c in col).strip() for col in temp_df.columns.values]
                    
                    # 只要欄位名稱包含「當月營收」就是我們要的表
                    if any('當月營收' in str(col) for col in temp_df.columns):
                        df = temp_df
                        break
                
                if df is None:
                    continue
                
                # 建立精確查找欄位的內部函式 (避免「去年當月營收」被誤判為「當月營收」)
                def get_val_exact(row, include_kw, exclude_kw=None):
                    for col_name in row.index:
                        c_str = str(col_name)
                        if include_kw in c_str:
                            if exclude_kw and exclude_kw in c_str:
                                continue
                            return self._clean_number(row[col_name])
                    return None

                for idx, row in df.iterrows():
                    first_col_val = str(row.iloc[0]).strip()
                    month = None
                    
                    # 解析月份欄位 (可能格式: "112/01", "1", "01月")
                    if '/' in first_col_val:
                        parts = first_col_val.split('/')
                        if len(parts) == 2 and parts[1].isdigit():
                            month = int(parts[1])
                    else:
                        m_str = first_col_val.replace('月', '')
                        if m_str.isdigit():
                            month = int(m_str)
                            
                    if month is None or not (1 <= month <= 12):
                        continue
                        
                    period_date = f"{y}-{month:02d}-01"
                    
                    # 透過關鍵字模糊抓取欄位
                    current_rev = get_val_exact(row, '當月營收', '去年')
                    mom = get_val_exact(row, '上月比較增減')
                    ly_rev = get_val_exact(row, '去年當月營收')
                    yoy = get_val_exact(row, '去年同月增減')
                    acc_rev = get_val_exact(row, '當月累計營收', '去年')
                    ly_acc = get_val_exact(row, '去年累計營收')
                    acc_yoy = get_val_exact(row, '前期比較增減')
                    
                    if current_rev is not None:
                        results.append((
                            stock_id, period_date, current_rev, mom, ly_rev, 
                            yoy, acc_rev, ly_acc, acc_yoy
                        ))
            except Exception as e:
                print(f"[警告] 抓取 {y} 年公開資訊觀測站營收發生錯誤: {e}")
                
        # 依照日期排序（由新到舊），並根據使用者選擇的 period 數量返回
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:months_to_fetch]

    def _safe_get(self, df, col, key):
        if key in df.index:
            val = df.at[key, col]
            return None if pd.isna(val) else int(val)
        return None

    def fetch_financials(self, stock_id, period="1y"):
        yf_ticker = f"{stock_id}.TW"
        ticker = yf.Ticker(yf_ticker)
        
        income = ticker.quarterly_financials
        balance = ticker.quarterly_balance_sheet
        cashflow = ticker.quarterly_cashflow
        
        # 1. 抓取 MOPS 月營收
        monthly_revenue_data = self._fetch_mops_monthly_revenue(stock_id, period)
        
        # yfinance 的日期篩選計算
        cutoff_date = datetime.now()
        if period == "1mo": cutoff_date -= timedelta(days=30)
        elif period == "1q": cutoff_date -= timedelta(days=90)
        elif period == "6mo": cutoff_date -= timedelta(days=180)
        else: cutoff_date -= timedelta(days=365) # 1y

        results = {
            "income": [],
            "balance": [],
            "cashflow": [],
            "monthly_revenue": monthly_revenue_data, # 寫入 MOPS 資料
            "quarterly_eps": []
        }

        # 處理損益表與單季EPS
        if not income.empty:
            for date in income.columns:
                if date >= pd.Timestamp(cutoff_date):
                    date_str = date.strftime('%Y-%m-%d')
                    results["income"].append((
                        stock_id, date_str,
                        self._safe_get(income, date, "Total Revenue"),
                        self._safe_get(income, date, "Gross Profit"),
                        self._safe_get(income, date, "Operating Expense"),
                        self._safe_get(income, date, "Operating Income"),
                        self._safe_get(income, date, "Net Income")
                    ))
                    
                    eps_val = self._safe_get(income, date, "Basic EPS")
                    if eps_val is not None:
                        results["quarterly_eps"].append((
                            stock_id, date_str, float(eps_val), None, None, None
                        ))

        # 處理資產負債表
        if not balance.empty:
            for date in balance.columns:
                if date >= pd.Timestamp(cutoff_date):
                    results["balance"].append((
                        stock_id, date.strftime('%Y-%m-%d'),
                        self._safe_get(balance, date, "Total Assets"),
                        self._safe_get(balance, date, "Total Liabilities Net Minority Interest"),
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
                        self._safe_get(cashflow, date, "Net Income") 
                    ))

        return results
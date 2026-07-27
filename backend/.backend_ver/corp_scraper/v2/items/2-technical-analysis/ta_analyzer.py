import yfinance as yf
import twstock
import pandas as pd
import numpy as np
import datetime
from googletrans import Translator

class TAAnalyzer:
    def __init__(self):
        self.translator = Translator()

    def get_yf_stock_id(self, stock_id):
        """透過 twstock 判斷台灣上市/上櫃代碼"""
        if stock_id in twstock.codes:
            market = twstock.codes[stock_id].market
            return f"{stock_id}.TW" if market == "上市" else f"{stock_id}.TWO"
        return f"{stock_id}.TW"

    def fetch_company_info(self, stock_id):
        """抓取並翻譯公司簡介 (英轉中)"""
        yf_stock_id = self.get_yf_stock_id(stock_id)
        ticker = yf.Ticker(yf_stock_id)
        
        info = ticker.info
        name = info.get("shortName", stock_id)
        summary_en = info.get("longBusinessSummary", "")
        
        if not summary_en:
            return name, "無英文簡介可供翻譯。"
            
        try:
            summary_zh = self.translator.translate(summary_en, src='en', dest='zh-tw').text
        except Exception as e:
            summary_zh = f"[翻譯失敗] {e}\n原文: {summary_en}"
            
        return name, summary_zh

    def calculate_ta(self, stock_id, period_str):
        """抓取資料並計算技術指標，最後根據使用者指定的 period_str 進行資料篩選"""
        yf_stock_id = self.get_yf_stock_id(stock_id)
        ticker = yf.Ticker(yf_stock_id)
        
        # 強制抓取 1 年歷史資料，確保長天期均線與 MACD 計算有足夠的前置數據
        df = ticker.history(period="1y")
        if df.empty:
            return None

        df = df.reset_index()
        df['Date'] = pd.to_datetime(df['Date']).dt.date

        # === 計算技術分析指標 ===
        # 1. KD, J (9日)
        low_9 = df['Low'].rolling(9, min_periods=1).min()
        high_9 = df['High'].rolling(9, min_periods=1).max()
        rsv = (df['Close'] - low_9) / (high_9 - low_9 + 1e-8) * 100
        df['K'] = rsv.ewm(com=2, adjust=False).mean()
        df['D'] = df['K'].ewm(com=2, adjust=False).mean()
        df['J'] = 3 * df['K'] - 2 * df['D']

        # 2. MACD (12, 26, 9)
        ema12 = df['Close'].ewm(span=12, adjust=False).mean()
        ema26 = df['Close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema12 - ema26
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()

        # 3. 乖離率 BIAS (6日)
        ma6 = df['Close'].rolling(6, min_periods=1).mean()
        df['BIAS'] = (df['Close'] - ma6) / ma6 * 100

        # 4. 威廉指標 Williams %R (14日)
        high_14 = df['High'].rolling(14, min_periods=1).max()
        low_14 = df['Low'].rolling(14, min_periods=1).min()
        df['Williams_R'] = (high_14 - df['Close']) / (high_14 - low_14 + 1e-8) * -100

        # 5. 多空指標 BBI (3,6,12,24)
        ma3 = df['Close'].rolling(3, min_periods=1).mean()
        ma12 = df['Close'].rolling(12, min_periods=1).mean()
        ma24 = df['Close'].rolling(24, min_periods=1).mean()
        df['BBI'] = (ma3 + ma6 + ma12 + ma24) / 4

        # 6. CDP 逆勢操作系統 (前一日)
        prev_h, prev_l, prev_c = df['High'].shift(1), df['Low'].shift(1), df['Close'].shift(1)
        df['CDP'] = (prev_h + prev_l + 2 * prev_c) / 4
        df['AH'] = df['CDP'] + (prev_h - prev_l)
        df['NH'] = 2 * df['CDP'] - prev_l
        df['NL'] = 2 * df['CDP'] - prev_h
        df['AL'] = df['CDP'] - (prev_h - prev_l)

        # 7. DMI 動向指標 (14日)
        up_move = df['High'] - df['High'].shift(1)
        down_move = df['Low'].shift(1) - df['Low']
        pdm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        mdm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        tr = pd.concat([
            df['High'] - df['Low'], 
            (df['High'] - df['Close'].shift(1)).abs(), 
            (df['Low'] - df['Close'].shift(1)).abs()
        ], axis=1).max(axis=1)
        
        atr = tr.rolling(14, min_periods=1).mean()
        df['PDI'] = pd.Series(pdm).rolling(14, min_periods=1).mean() / atr * 100
        df['MDI'] = pd.Series(mdm).rolling(14, min_periods=1).mean() / atr * 100
        dx = (df['PDI'] - df['MDI']).abs() / (df['PDI'] + df['MDI'] + 1e-8) * 100
        df['ADX'] = dx.rolling(14, min_periods=1).mean()

        # === 根據使用者要求過濾日期 ===
        today = datetime.date.today()
        days_to_keep = {'1wk': 7, '1mo': 30, '3mo': 90, '1y': 365}.get(period_str, 30)
        start_date = today - datetime.timedelta(days=days_to_keep)
        
        df_filtered = df[df['Date'] >= start_date].copy()
        return df_filtered
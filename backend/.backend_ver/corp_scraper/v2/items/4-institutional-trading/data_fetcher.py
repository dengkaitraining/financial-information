import yfinance as yf
import twstock
import pandas as pd
from googletrans import Translator
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
import random
import requests, time, json
from io import StringIO

class StockDataFetcher:
    def __init__(self):
        self.translator = Translator()

    def get_start_date(self, period):
        now = datetime.now()
        #"""
        if period == '1M': return now - relativedelta(months=1)
        elif period == '1Q': return now - relativedelta(months=3)
        elif period == '6M': return now - relativedelta(months=6)
        elif period == '1Y': return now - relativedelta(years=1)
        #"""
        """
        if period == '1Y': return now - relativedelta(years=1)
        elif period == '2Y': return now - relativedelta(years=2)
        elif period == '3Y': return now - relativedelta(years=3)
        elif period == '4Y': return now - relativedelta(years=4)
        """
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
    # --- 輔助函式 (可放在類別內或外部) ---
    # --- 加入 @staticmethod 修正這個錯誤 ---
    @staticmethod
    def _clean_twse_number(num_str):
        """清除 TWSE 數字字串中的逗號並轉換為 float 或 int"""
        if not num_str or num_str.strip() in ['', 'X', '-']:
            return 0
        try:
            cleaned = str(num_str).replace(',', '').strip()
            return float(cleaned) if '.' in cleaned else int(cleaned)
        except ValueError:
            return 0
    # --- 加入 @staticmethod 修正這個錯誤 ---
    @staticmethod
    def _tw_date_to_gregorian(tw_date_str):
        """將民國年(如 115/07/27) 轉換為 datetime.date 物件"""
        parts = tw_date_str.split('/')
        if len(parts) == 3:
            year = int(parts[0]) + 1911
            return datetime(year, int(parts[1]), int(parts[2])).date()
        return None
    # ----------------------------------

    # 將以下函式替換 data_fetcher.py 中原有的 fetch_daily_trading_margin 模擬函式
    def fetch_daily_trading_margin(self, stock_id, period):
        """
        2. 真實抓取：法人逐日買賣超 & 資券餘額 (使用 TWSE API)
        """
        print(f"\n[TWSE API] 開始抓取 {stock_id} 的法人與資券餘額資料...")
        print("⚠️ 提醒：為避免證交所封鎖 IP，每次請求將暫停 3 秒，抓取長區間可能需要數分鐘。")
        
        start_date = self.get_start_date(period).date()
        end_date = datetime.now().date()
        
        print(f"start_date => {start_date}")
        print(f"end_date => {end_date}")

        records = []
        
        # 建立 requests Session 並偽裝 Header 避免被擋
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # === 步驟一：按「月」抓取價量資料 (STOCK_DAY) ===
        monthly_price_data = {}
        current_month_start = start_date.replace(day=1)
        
        while current_month_start <= end_date:
            # TWSE 參數格式為 YYYYMMDD (例如 20260701)
            date_param = current_month_start.strftime('%Y%m01')
            url_stock_day = f"https://www.twse.com.tw/rwd/zh/afterTrading/STOCK_DAY?date={date_param}&stockNo={stock_id}"
            
            try:
                print(f"  -> 抓取價量資料: {current_month_start.strftime('%Y-%m')}")
                res = session.get(url_stock_day, timeout=10)
                data = res.json()
                
                if data.get('stat') == 'OK':
                    for row in data.get('data', []):
                        dt = self._tw_date_to_gregorian(row[0])
                        if dt and start_date <= dt <= end_date:
                            # 漲跌幅計算 = (漲跌價差 / (收盤價 - 漲跌價差)) * 100
                            diff = self._clean_twse_number(row[7].replace('+', '')) 
                            close = self._clean_twse_number(row[6])
                            prev_close = close - diff
                            pct_change = round((diff / prev_close) * 100, 2) if prev_close else 0.0
                            
                            monthly_price_data[dt] = {
                                'volume': int(self._clean_twse_number(row[1]) / 1000), # 股轉張
                                'price_change_pct': pct_change
                            }
            except Exception as e:
                print(f"  [錯誤] 抓取 {date_param} 價量失敗: {e}")
                
            # 推進到下個月
            current_month_start += relativedelta(months=1)
            time.sleep(5) # 防 Ban

        # === 步驟二：依據有開市的日期，逐日抓取法人與資券 (T86, MI_MARGN, MI_QFIIS) ===
        # 這裡以 monthly_price_data 的 keys 為準，因為那是台股確定有交易的日子
        trading_days = sorted(list(monthly_price_data.keys()))
        
        for dt in trading_days:
            date_param = dt.strftime('%Y%m%d')
            print(f"  -> 抓取法人與資券資料: {date_param} ... ", end="")
            
            # 預設數值
            f_vol = t_vol = d_vol = total_vol = 0
            margin_bal = short_bal = f_ratio = 0
            lending_bal = 0 # 借券餘額通常需查另一個 API (TWT93U)，此處簡化預設為0，避免請求過多
            
            try:
                # 1. 三大法人買賣超 (T86)
                url_t86 = f"https://www.twse.com.tw/rwd/zh/fund/T86?date={date_param}&selectType=ALL"
                res_t86 = session.get(url_t86, timeout=10).json()
                if res_t86.get('stat') == 'OK':
                    # 尋找該股票的列
                    for row in res_t86.get('data', []):
                        if row[0] == stock_id:
                            # TWSE 欄位：4=外資買賣超, 10=投信買賣超, 11=自營買賣超, 18=合計 (皆為股數，需轉張)
                            f_vol = int(self._clean_twse_number(row[4]) / 1000)
                            t_vol = int(self._clean_twse_number(row[10]) / 1000)
                            d_vol = int(self._clean_twse_number(row[11]) / 1000)
                            total_vol = f_vol + t_vol + d_vol
                            break
                time.sleep(5) # 防 Ban

                # 2. 融資融券餘額 (MI_MARGN)
                url_margin = f"https://www.twse.com.tw/rwd/zh/marginTrading/MI_MARGN?date={date_param}&selectType=ALL"
                res_margin = session.get(url_margin, timeout=10).json()
                if res_margin.get('stat') == 'OK':
                    for row in res_margin.get('data', []):
                        if row[0] == stock_id:
                            # TWSE 欄位：6=融資今日餘額(張), 12=融券今日餘額(張)
                            margin_bal = int(self._clean_twse_number(row[6]))
                            short_bal = int(self._clean_twse_number(row[12]))
                            break
                time.sleep(5) # 防 Ban
                
                # 3. 外資持股比例 (MI_QFIIS)
                url_qfiis = f"https://www.twse.com.tw/rwd/zh/fund/MI_QFIIS?date={date_param}&selectType=ALL"
                res_qfiis = session.get(url_qfiis, timeout=10).json()
                if res_qfiis.get('stat') == 'OK':
                    for row in res_qfiis.get('data', []):
                        if row[0] == stock_id:
                            # TWSE 欄位: 10 = 外資持股比例 (%)
                            f_ratio = round(float(self._clean_twse_number(row[10])), 2)
                            break
                time.sleep(5) # 防 Ban
                
                print("OK")
                
            except Exception as e:
                print(f"失敗 ({e})")
            
            # 整合當日資料
            price_info = monthly_price_data[dt]
            records.append((
                stock_id, 
                dt, 
                f_vol, t_vol, d_vol, total_vol, 
                f_ratio, 
                price_info['price_change_pct'], 
                price_info['volume'], 
                margin_bal, short_bal, lending_bal
            ))

        return records
    # (2026-07-27) fetch_daily_trading_margin --- { end } ----

    # (2026-07-27) fetch_major_players --- { start } ----
    def fetch_major_players(self, stock_id, period):
        """
        3. 透過 TWSE 證交所官方 API 抓取「三大法人買賣超 (T86)」
        將外資、投信、自營商視為主要的大型機構，寫入主力進出表。
        """
        print(f"正在透過 TWSE API 抓取 {stock_id} 官方三大法人進出資料...")
        
        start_date = self.get_start_date(period).date()
        end_date = datetime.now().date()
        
        # 產生需要抓取的日期清單 (排除六日)
        dates_to_fetch = []
        current = start_date
        while current <= end_date:
            if current.weekday() < 5:  # 0-4 為週一到週五
                dates_to_fetch.append(current)
            current += timedelta(days=1)

        records = []
        
        # 證交所 API 網址 (三大法人買賣超日報)
        base_url = "https://www.twse.com.tw/fund/T86"
        
        for d in dates_to_fetch:
            # TWSE API 日期格式要求為 YYYYMMDD，但民國年不強制，西元年也通
            date_str = d.strftime("%Y%m%d")
            
            # selectType=ALL 代表抓取全市場，再從中篩選我們的 stock_id
            params = {
                "response": "json",
                "date": date_str,
                "selectType": "ALL"
            }
            
            try:
                res = requests.get(base_url, params=params, timeout=10)
                data = res.json()
                
                # 檢查當天是否有資料 (如遇國定假日則 stat 會是 '很抱歉，沒有符合條件的資料!')
                if data.get('stat') != 'OK':
                    print(f"  - {date_str}: 無交易資料或為假日休市")
                    time.sleep(5) # 即使沒資料也要暫停，避免被 ban
                    continue
                
                fields = data.get('fields', [])
                data_list = data.get('data', [])
                
                # 尋找目標股票
                target_row = next((row for row in data_list if row[0] == stock_id), None)
                
                if target_row:
                    # TWSE 欄位順序對應 (可能隨證交所改版微調，需注意)
                    # 依據目前規格：[0]代號 [1]名稱 [2]外資買進 [3]外資賣出 [4]外資買賣超 ...
                    # 股數轉張數需除以 1000
                    
                    try:
                        # 處理字串轉數字，移除逗號
                        def to_vol(val_str):
                            return int(val_str.replace(',', '')) // 1000

                        # 1. 外資 (包含外資及陸資、外資自營商)
                        f_buy = to_vol(target_row[2])
                        f_sell = to_vol(target_row[3])
                        f_net = f_buy - f_sell
                        records.append((stock_id, d, '外資', 'BUY' if f_net > 0 else 'SELL', f_buy, f_sell, f_net))

                        # 2. 投信
                        t_buy = to_vol(target_row[8])
                        t_sell = to_vol(target_row[9])
                        t_net = t_buy - t_sell
                        records.append((stock_id, d, '投信', 'BUY' if t_net > 0 else 'SELL', t_buy, t_sell, t_net))

                        # 3. 自營商 (自行買賣 + 避險)
                        d_buy = to_vol(target_row[11]) + to_vol(target_row[14])
                        d_sell = to_vol(target_row[12]) + to_vol(target_row[15])
                        d_net = d_buy - d_sell
                        records.append((stock_id, d, '自營商', 'BUY' if d_net > 0 else 'SELL', d_buy, d_sell, d_net))
                        
                        print(f"  - {date_str}: 成功抓取 {stock_id} 籌碼資料")
                    except Exception as parse_err:
                        print(f"  - {date_str}: 資料解析錯誤 {parse_err}")
                else:
                    print(f"  - {date_str}: 找不到 {stock_id} 的資料")
                    
            except Exception as e:
                print(f"[錯誤] {date_str} 請求失敗: {e}")
            
            # 【絕對必要】延遲 3 到 5 秒，證交所對連續 Request 的阻斷非常嚴格
            time.sleep(5)
            
        return records
    # (2026-07-27) fetch_major_players --- { end } ----

    # (2026-07-27) fetch_large_shareholders --- { start } ----
    def fetch_large_shareholders(self, stock_id, period):
        """
        4. 抓取大戶籌碼與董監持股 (真實 requests 爬蟲版)
        使用 yfinance 取得股價，並透過 requests 解析 MOPS(公開資訊觀測站) 與 集保(TDCC) 資訊。
        """
        print(f"\n正在抓取 {stock_id} 大戶籌碼與董監持股 (需時較長，請稍候)...")
        start_date = self.get_start_date(period)
        
        # 1. 取得歷史股價 (利用 yfinance)
        ticker = yf.Ticker(f"{stock_id}.TW")
        hist = ticker.history(start=start_date.strftime('%Y-%m-%d'))
        
        if hist.empty:
            print(f"無法取得 {stock_id} 的 yfinance 股價資料。")
            return []

        # 大戶籌碼通常是每週五公佈，因此我們將日線資料轉換為每週五的資料
        hist_weekly = hist.resample('W-FRI').last()
        records = []

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        for date_idx, row in hist_weekly.iterrows():
            trade_date = date_idx.date()
            if trade_date > datetime.now().date():
                continue
                
            price = round(row.get('Close', 0.0), 2)
            
            # --- 2. 抓取公開資訊觀測站 (MOPS) - 董監持股 ---
            # 董監持股為月報，我們根據 trade_date 推算對應的民國年月 (通常查閱上個月)
            year_tw = trade_date.year - 1911
            month = trade_date.month - 1 if trade_date.month > 1 else 12
            if month == 12: year_tw -= 1
            
            director_ratio = 0.0
            try:
                mops_url = "https://mops.twse.com.tw/mops/web/ajax_t165sb02"
                payload = {
                    'encodeURIComponent': '1',
                    'step': '1',
                    'firstin': '1',
                    'off': '1',
                    'queryName': 'co_id',
                    'inpuType': 'co_id',
                    'TYPEK': 'all',
                    'isnew': 'false',
                    'co_id': stock_id,
                    'year': str(year_tw),
                    'month': str(month).zfill(2)
                }
                mops_res = requests.post(mops_url, data=payload, headers=headers, timeout=5)
                if mops_res.status_code == 200:
                    #dfs = pd.read_html(mops_res.text)
                    # 使用 StringIO 包裝 HTML 字串
                    dfs = pd.read_html(StringIO(mops_res.text))
                    if len(dfs) > 0:
                        # 依據 MOPS 結構，通常最後一欄是「董監事持股成數」或類似字眼
                        # 這裡抓取一個範例數值 (實務上需根據實際 DataFrame 的 index 定位)
                        # 為避免結構變動報錯，加上基礎防呆
                        for df in dfs:
                            if '持股成數' in df.to_string():
                                director_ratio = float(df.iloc[-1, -1]) if not pd.isna(df.iloc[-1, -1]) else 0.0
                                break
            except Exception as e:
                print(f"MOPS 董監持股解析失敗 ({trade_date}): {e}")

            # --- 3. 抓取集保中心 (TDCC) - 大戶籌碼 ---
            # 大戶籌碼定義：我們以持有 > 1000 張 (級距 15) 的比例作為大戶籌碼
            # 注意：集保中心歷史資料查詢常常需要對應精確的星期五日期字串格式 (YYYYMMDD)
            date_str = trade_date.strftime('%Y%m%d')
            large_holder_ratio = 0.0
            
            try:
                tdcc_url = f"https://www.tdcc.com.tw/smWeb/QryStockAjax.do"
                tdcc_payload = {
                    'scaDates': date_str,
                    'scaDate': date_str,
                    'SqlMethod': 'StockNo',
                    'StockNo': stock_id,
                    'req': '查詢'
                }
                tdcc_res = requests.post(tdcc_url, data=tdcc_payload, headers=headers, timeout=5)
                
                if tdcc_res.status_code == 200 and "查無資料" not in tdcc_res.text:
                    #tdcc_dfs = pd.read_html(tdcc_res.text)
                    # 使用 StringIO 包裝 HTML 字串
                    tdcc_dfs = pd.read_html(StringIO(tdcc_res.text))
                    if len(tdcc_dfs) >= 7: # 集保資料表通常在第 7 個 table
                        df_tdcc = tdcc_dfs[6]
                        # 第 15 級距是 "1,000,001以上"，對應的比例通常在最後一欄
                        large_holder_row = df_tdcc[df_tdcc.iloc[:, 0].astype(str) == '15']
                        if not large_holder_row.empty:
                            ratio_str = large_holder_row.iloc[0, -1]
                            large_holder_ratio = float(ratio_str)
            except Exception as e:
                # 歷史集保資料可能被 TDCC 移至其他端點，報錯是正常現象
                print(f"TDCC 集保籌碼解析失敗 ({trade_date}): {e}")
                
            # 模擬外資比例 (實務需由三大法人買賣超累積計算，或 yfinance % Out)
            foreign_ratio = 0.0 
            
            records.append((
                stock_id, 
                trade_date,
                foreign_ratio, 
                large_holder_ratio, 
                director_ratio, 
                price
            ))
            
            # 延遲 1 秒，避免被 MOPS 與 TDCC 防火牆阻擋 (Rate Limit)
            time.sleep(5)

        print(f"大戶籌碼與董監持股抓取完畢，共 {len(records)} 筆。")
        return records
    # (2026-07-27) fetch_large_shareholders --- { end } ----
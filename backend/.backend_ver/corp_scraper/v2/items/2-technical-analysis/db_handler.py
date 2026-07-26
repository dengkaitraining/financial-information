# db.py
import MySQLdb
import numpy as np

class DBHandler:
    def __init__(self, host='127.0.0.1', user='root', password='your_password', database='stock_db'):
        # ⚠️ 請將 password 替換為您的 MariaDB 密碼
        self.config = {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8mb4'
        }

    def get_connection(self):
        """建立並回傳資料庫連線"""
        return MySQLdb.connect(**self.config)

    def save_ta_data(self, symbol, df):
        """寫入技術分析資料，遇到重複主鍵則更新"""
        if df is None or df.empty:
            return False, "沒有抓取到技術分析資料，取消寫入。"

        # 將 Pandas 的 NaN 轉為 None 以符合 MySQL NULL 格式
        df = df.replace({np.nan: None})

        conn = self.get_connection()
        cursor = conn.cursor()

        sql = """
            INSERT INTO technical_analysis (
                symbol, trade_date, volume, open_price, high_price, low_price, close_price,
                k_value, d_value, j_value, macd, macd_signal, bias, williams_r, bbi,
                cdp, ah, nh, nl, al, pdi, mdi, adx
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) ON DUPLICATE KEY UPDATE 
                volume=VALUES(volume), open_price=VALUES(open_price), high_price=VALUES(high_price),
                low_price=VALUES(low_price), close_price=VALUES(close_price),
                k_value=VALUES(k_value), d_value=VALUES(d_value), j_value=VALUES(j_value),
                macd=VALUES(macd), macd_signal=VALUES(macd_signal), bias=VALUES(bias), 
                williams_r=VALUES(williams_r), bbi=VALUES(bbi), cdp=VALUES(cdp), 
                ah=VALUES(ah), nh=VALUES(nh), nl=VALUES(nl), al=VALUES(al), 
                pdi=VALUES(pdi), mdi=VALUES(mdi), adx=VALUES(adx)
        """
        
        data_tuples = []
        for _, row in df.iterrows():
            data_tuples.append((
                symbol, row['Date'], row['Volume'], row['Open'], row['High'], row['Low'], row['Close'],
                row['K'], row['D'], row['J'], row['MACD'], row['MACD_Signal'], row['BIAS'], 
                row['Williams_R'], row['BBI'], row['CDP'], row['AH'], row['NH'], row['NL'], 
                row['AL'], row['PDI'], row['MDI'], row['ADX']
            ))

        try:
            cursor.executemany(sql, data_tuples)
            conn.commit()
            row_count = cursor.rowcount
            return True, f"成功寫入或更新了 {row_count} 筆資料。"
        except Exception as e:
            conn.rollback()
            return False, f"資料庫寫入失敗: {e}"
        finally:
            cursor.close()
            conn.close()
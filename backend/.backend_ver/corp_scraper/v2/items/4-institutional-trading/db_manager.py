import MySQLdb

class DBManager:
    def __init__(self, host='localhost', user='root', password='your_password', db='stock_db'):
        self.conn_params = {
            'host': host,
            'user': user,
            'passwd': password,
            'db': db,
            'charset': 'utf8mb4'
        }

    def get_connection(self):
        return MySQLdb.connect(**self.conn_params)

    def _execute_many(self, sql, records):
        """內部共用的批次執行方法"""
        if not records:
            return 0
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(sql, records)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            print(f"資料庫寫入錯誤: {e}")
            return 0

    def upsert_yfinance_data(self, records):
        sql = """
            INSERT INTO yfinance_institutional 
            (stock_id, date_reported, holder_name_en, holder_name_zh, shares, out_ratio, value)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            holder_name_zh=VALUES(holder_name_zh),
            shares=VALUES(shares),
            out_ratio=VALUES(out_ratio),
            value=VALUES(value)
        """
        return self._execute_many(sql, records)

    def upsert_daily_institutional_trading(self, records):
        sql = """
            INSERT INTO daily_institutional_trading 
            (stock_id, trade_date, foreign_vol, trust_vol, dealer_vol, total_vol, 
             foreign_ratio, price_change_pct, volume, margin_balance, short_balance, lending_balance)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            foreign_vol=VALUES(foreign_vol),
            trust_vol=VALUES(trust_vol),
            dealer_vol=VALUES(dealer_vol),
            total_vol=VALUES(total_vol),
            foreign_ratio=VALUES(foreign_ratio),
            price_change_pct=VALUES(price_change_pct),
            volume=VALUES(volume),
            margin_balance=VALUES(margin_balance),
            short_balance=VALUES(short_balance),
            lending_balance=VALUES(lending_balance)
        """
        return self._execute_many(sql, records)

    def upsert_major_players_trading(self, records):
        sql = """
            INSERT INTO major_players_trading 
            (stock_id, trade_date, broker_name, trade_type, buy_vol, sell_vol, net_vol)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            buy_vol=VALUES(buy_vol),
            sell_vol=VALUES(sell_vol),
            net_vol=VALUES(net_vol)
        """
        return self._execute_many(sql, records)

    def upsert_large_shareholders(self, records):
        sql = """
            INSERT INTO large_shareholders 
            (stock_id, record_date, foreign_ratio, large_holder_ratio, director_ratio, stock_price)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            foreign_ratio=VALUES(foreign_ratio),
            large_holder_ratio=VALUES(large_holder_ratio),
            director_ratio=VALUES(director_ratio),
            stock_price=VALUES(stock_price)
        """
        return self._execute_many(sql, records)
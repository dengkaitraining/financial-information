import MySQLdb

class StockDatabase:
    def __init__(self, host="localhost", user="root", password="password", db="stock_db"):
        self.conn = MySQLdb.connect(
            host=host,
            user=user,
            passwd=password,
            db=db,
            charset='utf8mb4'
        )
        self.cursor = self.conn.cursor()

    def insert_income_statement(self, data_list):
        if not data_list:
            return
        sql = """
            INSERT INTO income_statement 
            (stock_id, period_date, revenue, gross_profit, operating_expense, operating_income, net_income)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            revenue=VALUES(revenue), gross_profit=VALUES(gross_profit),
            operating_expense=VALUES(operating_expense), operating_income=VALUES(operating_income),
            net_income=VALUES(net_income)
        """
        self.cursor.executemany(sql, data_list)
        self.conn.commit()

    def insert_balance_sheet(self, data_list):
        if not data_list:
            return
        sql = """
            INSERT INTO balance_sheet 
            (stock_id, period_date, total_assets, total_liabilities, stockholders_equity, current_assets, current_liabilities)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            total_assets=VALUES(total_assets), total_liabilities=VALUES(total_liabilities),
            stockholders_equity=VALUES(stockholders_equity), current_assets=VALUES(current_assets),
            current_liabilities=VALUES(current_liabilities)
        """
        self.cursor.executemany(sql, data_list)
        self.conn.commit()

    def insert_cash_flow(self, data_list):
        if not data_list:
            return
        sql = """
            INSERT INTO cash_flow 
            (stock_id, period_date, operating_cf, investing_cf, financing_cf, free_cf, net_cf)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            operating_cf=VALUES(operating_cf), investing_cf=VALUES(investing_cf),
            financing_cf=VALUES(financing_cf), free_cf=VALUES(free_cf), net_cf=VALUES(net_cf)
        """
        self.cursor.executemany(sql, data_list)
        self.conn.commit()

    def insert_monthly_revenue(self, data_list):
        if not data_list:
            return
        sql = """
            INSERT INTO monthly_revenue 
            (stock_id, period_date, current_revenue, mom_percent, last_year_revenue, 
             yoy_percent, acc_revenue, last_year_acc_revenue, acc_yoy_percent)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            current_revenue=VALUES(current_revenue), mom_percent=VALUES(mom_percent),
            last_year_revenue=VALUES(last_year_revenue), yoy_percent=VALUES(yoy_percent),
            acc_revenue=VALUES(acc_revenue), last_year_acc_revenue=VALUES(last_year_acc_revenue),
            acc_yoy_percent=VALUES(acc_yoy_percent)
        """
        self.cursor.executemany(sql, data_list)
        self.conn.commit()

    def insert_quarterly_eps(self, data_list):
        if not data_list:
            return
        sql = """
            INSERT INTO quarterly_eps 
            (stock_id, period_date, eps, qoq_percent, yoy_percent, quarter_avg_price)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            eps=VALUES(eps), qoq_percent=VALUES(qoq_percent),
            yoy_percent=VALUES(yoy_percent), quarter_avg_price=VALUES(quarter_avg_price)
        """
        self.cursor.executemany(sql, data_list)
        self.conn.commit()

    def close(self):
        self.cursor.close()
        self.conn.close()
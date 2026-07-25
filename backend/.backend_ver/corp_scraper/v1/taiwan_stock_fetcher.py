# 檔案名稱: taiwan_stock_fetcher.py

import json
from datetime import datetime
from FinMind.data import DataLoader
import pandas as pd
import pymysql
import yfinance as yf

class TaiwanStockDataFetcher:
    """台灣股票公司詳細資訊抓取與資料庫維護類別 (整合 FinMind, yfinance 與 MariaDB 12.3)"""

    def __init__(self, db_config: dict = None, finmind_token: str = ""):
        self.dl = DataLoader()
        if finmind_token:
            self.dl.login_by_token(finmind_token)
        self.db_config = db_config

    def _get_db_connection(self):
        """建立 MariaDB 資料庫連線"""
        if not self.db_config:
            raise ValueError("未設定 MariaDB 連線參數！")
        return pymysql.connect(
            host=self.db_config.get("host", "localhost"),
            port=self.db_config.get("port", 3306),
            user=self.db_config.get("user", "root"),
            password=self.db_config.get("password", ""),
            database=self.db_config.get("database", "tw_stock_analysis"),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )

    # ------------------------------------------------------------------
    # 1. 抓取模組 (Fetch Methods)
    # ------------------------------------------------------------------

    def fetch_company_profile(self, stock_id: str) -> dict:
        """1. 抓取公司基本面資料"""
        ticker_symbol = f"{stock_id}.TW"  # 預設上市，若失敗可延伸改 .TWO (上櫃)
        yf_ticker = yf.Ticker(ticker_symbol)
        info = yf_ticker.info

        # 透過 FinMind 取得補充資訊 (如成立/上市日期)
        info_df = self.dl.taiwan_stock_info()
        stock_info = info_df[info_df["stock_id"] == stock_id]

        profile = {
            "stock_id": stock_id,
            "company_name": info.get(
                "longName",
                stock_info["stock_name"].values[0] if not stock_info.empty else stock_id,
            ),
            "industry_category": info.get(
                "industry",
                stock_info["industry_category"].values[0] if not stock_info.empty else "N/A",
            ),
            "capital": info.get("marketCap", None),
            "listing_date": stock_info["date"].values[0] if not stock_info.empty else None,
            "establishment_date": None,
            "description": info.get("longBusinessSummary", "無簡介"),
        }
        return profile

    def fetch_monthly_revenue(self, stock_id: str, start_date: str) -> list:
        """2. 抓取經營營運面 (月營收與 MoM/YoY)"""
        df = self.dl.taiwan_stock_month_revenue(stock_id=stock_id, start_date=start_date)
        if df.empty:
            return []

        # 排序並計算 MoM / YoY
        df["revenue_year"] = df["revenue_year"].astype(int)
        df["revenue_month"] = df["revenue_month"].astype(int)
        df = df.sort_values(["revenue_year", "revenue_month"])

        df["mom_growth"] = df["revenue"].pct_change() * 100
        df["yoy_growth"] = df["revenue"].pct_change(12) * 100

        result = []
        for _, row in df.iterrows():
            result.append(
                {
                    "stock_id": stock_id,
                    "revenue_year": int(row["revenue_year"]),
                    "revenue_month": int(row["revenue_month"]),
                    "revenue": int(row["revenue"]),
                    "mom_growth": round(float(row["mom_growth"]), 4) if pd.notnull(row["mom_growth"]) else None,
                    "yoy_growth": round(float(row["yoy_growth"]), 4) if pd.notnull(row["yoy_growth"]) else None,
                }
            )
        return result

    def fetch_financial_metrics(self, stock_id: str, start_date: str) -> list:
        """3. 抓取財務獲利面 (EPS, 毛利率, 營業利益率, 負債比, ROE/ROA)"""
        df = self.dl.taiwan_stock_financial_statement(stock_id=stock_id, start_date=start_date)
        if df.empty:
            return []

        # 樞紐分析轉換科目為欄位
        pivot_df = df.pivot_table(index="date", columns="type", values="value", aggfunc="first").reset_index()

        metrics = []
        for _, row in pivot_df.iterrows():
            dt = datetime.strptime(row["date"], "%Y-%m-%d")
            quarter = (dt.month - 1) // 3 + 1

            metrics.append(
                {
                    "stock_id": stock_id,
                    "year": dt.year,
                    "quarter": quarter,
                    "eps": float(row.get("EPS", 0)) if pd.notnull(row.get("EPS")) else None,
                    "gross_margin": float(row.get("GrossProfitMargin", 0)) if pd.notnull(row.get("GrossProfitMargin")) else None,
                    "operating_margin": float(row.get("OperatingIncomeMargin", 0)) if pd.notnull(row.get("OperatingIncomeMargin")) else None,
                    "debt_ratio": float(row.get("LiabilityRatio", 0)) if pd.notnull(row.get("LiabilityRatio")) else None,
                    "roe": float(row.get("ROE", 0)) if pd.notnull(row.get("ROE")) else None,
                    "roa": float(row.get("ROA", 0)) if pd.notnull(row.get("ROA")) else None,
                }
            )
        return metrics

    def fetch_valuation_chip(self, stock_id: str, start_date: str) -> list:
        """4. 抓取估值與籌碼面 (PE, PB, 殖利率, 三大法人買賣超)"""
        per_df = self.dl.taiwan_stock_per_pbr(stock_id=stock_id, start_date=start_date)
        #chip_df = self.dl.taiwan_stock_institutional_investors_buy_sell(stock_id=stock_id, start_date=start_date)
        chip_df = self.dl.taiwan_stock_institutional_investors(stock_id=stock_id, start_date=start_date)

        merged_data = {}
        if not per_df.empty:
            for _, row in per_df.iterrows():
                date_str = row["date"]
                merged_data[date_str] = {
                    "stock_id": stock_id,
                    "trade_date": date_str,
                    "pe_ratio": float(row["PER"]) if pd.notnull(row.get("PER")) else None,
                    "pb_ratio": float(row["PBR"]) if pd.notnull(row.get("PBR")) else None,
                    "yield_rate": float(row["dividend_yield"]) if pd.notnull(row.get("dividend_yield")) else None,
                    "foreign_buy": 0,
                    "investment_trust_buy": 0,
                    "dealer_buy": 0,
                    "institutional_total_buy": 0,
                }

        if not chip_df.empty:
            for date_str, group in chip_df.groupby("date"):
                if date_str not in merged_data:
                    merged_data[date_str] = {
                        "stock_id": stock_id,
                        "trade_date": date_str,
                        "pe_ratio": None,
                        "pb_ratio": None,
                        "yield_rate": None,
                        "foreign_buy": 0,
                        "investment_trust_buy": 0,
                        "dealer_buy": 0,
                        "institutional_total_buy": 0,
                    }

                f_buy = group[group["name"].str.contains("Foreign", case=False, na=False)]["buy"].sum() - \
                        group[group["name"].str.contains("Foreign", case=False, na=False)]["sell"].sum()
                it_buy = group[group["name"].str.contains("Investment", case=False, na=False)]["buy"].sum() - \
                         group[group["name"].str.contains("Investment", case=False, na=False)]["sell"].sum()
                d_buy = group[group["name"].str.contains("Dealer", case=False, na=False)]["buy"].sum() - \
                        group[group["name"].str.contains("Dealer", case=False, na=False)]["sell"].sum()

                merged_data[date_str]["foreign_buy"] = int(f_buy)
                merged_data[date_str]["investment_trust_buy"] = int(it_buy)
                merged_data[date_str]["dealer_buy"] = int(d_buy)
                merged_data[date_str]["institutional_total_buy"] = int(f_buy + it_buy + d_buy)

        return list(merged_data.values())

    # ------------------------------------------------------------------
    # 2. 資料庫存入模組 (Save Methods to MariaDB 12.3)
    # ------------------------------------------------------------------

    def save_all_to_mariadb(self, full_data: dict):
        """將經過使用者確認後的資料寫入 MariaDB 資料庫"""
        conn = self._get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 1. 寫入 company_profile
                cp = full_data["profile"]
                sql_cp = """
                INSERT INTO company_profile (stock_id, company_name, industry_category, capital, listing_date, description)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    company_name=VALUES(company_name), 
                    industry_category=VALUES(industry_category),
                    capital=VALUES(capital),
                    listing_date=VALUES(listing_date),
                    description=VALUES(description);
                """
                cursor.execute(sql_cp, (cp["stock_id"], cp["company_name"], cp["industry_category"], cp["capital"], cp["listing_date"], cp["description"]))

                # 2. 寫入 monthly_revenue
                sql_rev = """
                INSERT INTO monthly_revenue (stock_id, revenue_year, revenue_month, revenue, mom_growth, yoy_growth)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    revenue=VALUES(revenue), mom_growth=VALUES(mom_growth), yoy_growth=VALUES(yoy_growth);
                """
                for rev in full_data["revenue"]:
                    cursor.execute(sql_rev, (rev["stock_id"], rev["revenue_year"], rev["revenue_month"], rev["revenue"], rev["mom_growth"], rev["yoy_growth"]))

                # 3. 寫入 financial_metrics
                sql_fin = """
                INSERT INTO financial_metrics (stock_id, year, quarter, eps, gross_margin, operating_margin, debt_ratio, roe, roa)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    eps=VALUES(eps), gross_margin=VALUES(gross_margin), operating_margin=VALUES(operating_margin),
                    debt_ratio=VALUES(debt_ratio), roe=VALUES(roe), roa=VALUES(roa);
                """
                for fin in full_data["financial"]:
                    cursor.execute(sql_fin, (fin["stock_id"], fin["year"], fin["quarter"], fin["eps"], fin["gross_margin"], fin["operating_margin"], fin["debt_ratio"], fin["roe"], fin["roa"]))

                # 4. 寫入 valuation_chip
                sql_vc = """
                INSERT INTO valuation_chip (stock_id, trade_date, pe_ratio, pb_ratio, yield_rate, foreign_buy, investment_trust_buy, dealer_buy, institutional_total_buy)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                    pe_ratio=VALUES(pe_ratio), pb_ratio=VALUES(pb_ratio), yield_rate=VALUES(yield_rate),
                    foreign_buy=VALUES(foreign_buy), investment_trust_buy=VALUES(investment_trust_buy),
                    dealer_buy=VALUES(dealer_buy), institutional_total_buy=VALUES(institutional_total_buy);
                """
                for vc in full_data["valuation"]:
                    cursor.execute(sql_vc, (vc["stock_id"], vc["trade_date"], vc["pe_ratio"], vc["pb_ratio"], vc["yield_rate"], vc["foreign_buy"], vc["investment_trust_buy"], vc["dealer_buy"], vc["institutional_total_buy"]))

            conn.commit()
            print("\n[SUCCESS] 資料已成功寫入 MariaDB 12.3 各維度表單中！")
        except Exception as e:
            conn.rollback()
            print(f"\n[ERROR] 資料庫寫入失敗: {e}")
        finally:
            conn.close()
# 檔案名稱: test_cli.py

# 引入核心模組
from taiwan_stock_fetcher import TaiwanStockDataFetcher
from dotenv import load_dotenv
import os

load_dotenv(".env")

def run_cli():
    print("=" * 60)
    print("  台灣股票公司詳細資訊抓取與檢視系統 (MariaDB 12.3 整合版)")
    print("=" * 60)

    stock_id = input("請輸入股票代號 (例如: 2330): ").strip()
    if not stock_id:
        stock_id = "2330"

    start_date = input("請輸入起始日期 (YYYY-MM-DD, 預設 2024-01-01): ").strip()
    if not start_date:
        start_date = "2024-01-01"

    # 初始化物件
    fetcher = TaiwanStockDataFetcher()

    print(f"\n正在抓取股票 [{stock_id}] 之四大維度資料，請稍候...")

    try:
        # 呼叫類別內的方法抓取資料
        profile = fetcher.fetch_company_profile(stock_id)
        #print(f"profile : [{profile}]")

        revenue = fetcher.fetch_monthly_revenue(stock_id, start_date)
        #print(f"revenue : [{revenue}]")

        financial = fetcher.fetch_financial_metrics(stock_id, start_date)
        #print(f"financial : [{financial}]")

        valuation = fetcher.fetch_valuation_chip(stock_id, start_date)
        #print(f"valuation : [{valuation}]")

        full_data = {
            "profile": profile,
            "revenue": revenue,
            "financial": financial,
            "valuation": valuation,
        }

        # 顯示資料摘要給使用者確認
        print("\n" + "=" * 20 + " 預覽抓取結果 " + "=" * 20)
        print(f"【1. 公司基本面】: {profile['company_name']} ({profile['stock_id']})")
        print(f"   產業: {profile['industry_category']} | 資本額/市值: {profile['capital']}")

        print(f"【2. 經營營運面】: 共抓取 {len(revenue)} 筆月營收紀錄")
        if revenue:
            latest_rev = revenue[-1]
            print(f"   最新月營收 ({latest_rev['revenue_year']}/{latest_rev['revenue_month']}): {latest_rev['revenue']:,} 元 (MoM: {latest_rev['mom_growth']}%, YoY: {latest_rev['yoy_growth']}%)")

        print(f"【3. 財務獲利面】: 共抓取 {len(financial)} 筆季度財務紀錄")
        if financial:
            latest_fin = financial[-1]
            print(f"   最新季度 ({latest_fin['year']} Q{latest_fin['quarter']}): EPS={latest_fin['eps']}, 毛利率={latest_fin['gross_margin']}%, ROE={latest_fin['roe']}%")

        print(f"【4. 估值與籌碼面】: 共抓取 {len(valuation)} 筆每日估值/籌碼紀錄")
        if valuation:
            latest_vc = valuation[-1]
            print(f"   最新交易日 ({latest_vc['trade_date']}): PE={latest_vc['pe_ratio']}, PB={latest_vc['pb_ratio']}, 三大法人買賣超={latest_vc['institutional_total_buy']} 股")

        print("=" * 54)

        # 詢問使用者是否寫入資料庫
        confirm = input("\n確認是否將上述資料寫入 MariaDB 資料庫？ (y/n): ").strip().lower()
        if confirm == "y":
            i_db_user = os.getenv("DB_USER")
            i_db_pass = os.getenv("DB_PASSWORD")

            db_host = input("請輸入 MariaDB Host (預設 localhost): ").strip() or "172.18.0.3"
            db_user = input("請輸入 MariaDB User (預設 root): ").strip() or str(i_db_user)
            db_pass = input("請輸入 MariaDB Password: ").strip() or str(i_db_pass)
            db_name = input("請輸入 Database 名稱 (預設 tw_stock_analysis): ").strip() or "tw_stock_analysis"

            # 設定資料庫連線資訊
            fetcher.db_config = {
                "host": db_host,
                "port": 3306,
                "user": db_user,
                "password": db_pass,
                "database": db_name,
            }

            print(f"db_config : {fetcher.db_config}")

            # 呼叫寫入方法
            fetcher.save_all_to_mariadb(full_data)
        else:
            print("\n已取消寫入動作。")

    except Exception as e:
        print(f"\n[ERROR] 執行過程發生錯誤: {e}")

if __name__ == "__main__":
    run_cli()
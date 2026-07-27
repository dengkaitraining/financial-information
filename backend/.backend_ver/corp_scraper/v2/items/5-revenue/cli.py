# ./ip_dc_all.sh
# ./enter_dc.sh
#
# fin_django_db
# mariadb -u root -p
#
# fin_django_backend
# cd .backend_ver/corp_scraper/v2/items/5-revenue
# python cli.py
#
# python /app/.backend_ver/corp_scraper/v2/items/5-revenue/cli.py
#
# cli.py
from db import StockDatabase
from fetcher import StockFetcher
from dotenv import load_dotenv
import os

load_dotenv(".env")

def main():
    print("=== Yahoo 股市風格財務資料抓取系統 ===")
    stock_id = input("請輸入台股代號 (例如 2330): ").strip()
    period = input("請選擇讀取時間 (1mo: 1個月, 1q: 1季, 6mo: 半年, 1y: 1年) [預設1y]: ").strip() or "1y"

    fetcher = StockFetcher()
    
    # 檢查股票是否存在
    is_valid, msg = fetcher.get_stock_info(stock_id)
    print(msg)
    if not is_valid: return

    print(f"\n正在從 yfinance 抓取 {stock_id} 近 {period} 財務資料...")
    data = fetcher.fetch_financials(stock_id, period)
    
    # 使用 Google 翻譯科目名稱供確認
    keys_to_translate = ["Total Revenue", "Gross Profit", "Operating Expense", "Operating Income", "Net Income"]
    translated_keys = fetcher.translate_keys(keys_to_translate)
    
    print("\n--- 抓取到的損益表資料範例 ---")
    for row in data['income']:
        print(f"日期: {row[1]}")
        print(f"  {translated_keys.get('Total Revenue', 'Total Revenue')}: {row[2]}")
        print(f"  {translated_keys.get('Gross Profit', 'Gross Profit')}: {row[3]}")
    
    confirm = input("\n請確認是否將以上資料寫入資料庫？(y/n): ").strip().lower()
    
    if confirm == 'y':
        db = None
        try:
            # 請修改為實際的資料庫帳號密碼
            db = StockDatabase(host="172.18.0.3", user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), db="stock_db")

            # 寫入五大表單資料
            db.insert_income_statement(data['income'])
            db.insert_balance_sheet(data['balance'])
            db.insert_cash_flow(data['cashflow'])
            
            # 新增的寫入功能
            db.insert_quarterly_eps(data['quarterly_eps'])
            db.insert_monthly_revenue(data['monthly_revenue'])
            
            print(f"\n✅ 資料已成功寫入，使用 ON DUPLICATE KEY UPDATE 確保無重複！")
            print(f"📊 本次寫入統整:")
            print(f" - 損益表: {len(data['income'])} 筆")
            print(f" - 資產負債表: {len(data['balance'])} 筆")
            print(f" - 現金流量表: {len(data['cashflow'])} 筆")
            print(f" - 單季EPS: {len(data['quarterly_eps'])} 筆")
            print(f" - 月營收: {len(data['monthly_revenue'])} 筆 (需另接 TWSE 訊號源)")
        except Exception as e:
            print(f"資料庫操作失敗: {e}")
        finally:
            if db:
                db.close()
    else:
        print("取消寫入資料庫。")

if __name__ == "__main__":
    main()
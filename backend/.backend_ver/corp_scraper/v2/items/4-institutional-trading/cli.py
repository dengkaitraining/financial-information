# ./ip_dc_all.sh
# ./enter_dc.sh
#
# fin_django_db
# mariadb -u root -p
#
# fin_django_backend
# cd .backend_ver/corp_scraper/v2/items/4-institutional-trading
# python cli.py
#
# python /app/.backend_ver/corp_scraper/v2/items/4-institutional-trading/cli.py
#
# cli.py
from data_fetcher import StockDataFetcher
from db_manager import DBManager
from dotenv import load_dotenv
import os

load_dotenv(".env")

def main():
    print("="*50)
    print(" 股市籌碼與主力進出系統整合測試 (CLI)")
    print("="*50)
    
    stock_id = input("請輸入股票代號 (如 2330): ").strip()
    print("\n資料讀取時間區間:")
    #"""
    print("1. 1個月 (1M)")
    print("2. 1季 (1Q)")
    print("3. 半年 (6M)")
    print("4. 1年 (1Y)")
    #"""
    """
    print("1. 1年 (1Y)")
    print("2. 2年 (2Y)")
    print("3. 3年 (3Y)")
    print("4. 4年 (4Y)")
    """

    choice = input("請選擇 (1-4): ").strip()
    period = {'1': '1M', '2': '1Q', '3': '6M', '4': '1Y'}.get(choice, '1M')
    #period = {'1': '1Y', '2': '2Y', '3': '3Y', '4': '4Y'}.get(choice, '1Y')

    fetcher = StockDataFetcher()
    
    # 抓取各項資料
    yfinance_data=[]
    daily_data=[]
    major_data=[]
    large_holder_data=[]
    print("\n--- 開始抓取資料 ---")
    yfinance_data = fetcher.fetch_yfinance_institutional(stock_id, period)
    daily_data = fetcher.fetch_daily_trading_margin(stock_id, period)
    major_data = fetcher.fetch_major_players(stock_id, period)
    large_holder_data = fetcher.fetch_large_shareholders(stock_id, period)

    if not any([yfinance_data, daily_data, major_data, large_holder_data]):
        print("\n未抓取到任何資料，程序結束。")
        return

    # 簡單預覽數量
    print("\n--- 資料抓取總結 ---")
    print(f"1. YFinance 國際法人持股: {len(yfinance_data)} 筆")
    print(f"2. 法人逐日買賣超 & 資券: {len(daily_data)} 筆")
    print(f"3. 主力進出 (券商分點): {len(major_data)} 筆")
    print(f"4. 大戶與董監持股: {len(large_holder_data)} 筆")

    confirm = input("\n確認是否將上述資料寫入 MariaDB stock_db？(y/n): ").strip().lower()
    
    if confirm == 'y':
        # 務必確認資料庫密碼正確
        db = DBManager(host='172.18.0.3', user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), db='stock_db')
        
        print("\n--- 開始寫入資料 ---")
        
        if yfinance_data:
            rows = db.upsert_yfinance_data(yfinance_data)
            print(f"[YFinance法人] 影響行數: {rows}")
            
        if daily_data:
            rows = db.upsert_daily_institutional_trading(daily_data)
            print(f"[逐日買賣超] 影響行數: {rows}")
            
        if major_data:
            rows = db.upsert_major_players_trading(major_data)
            print(f"[主力進出] 影響行數: {rows}")
            
        if large_holder_data:
            rows = db.upsert_large_shareholders(large_holder_data)
            print(f"[大戶籌碼] 影響行數: {rows}")
            
        print("\n寫入完成！已透過 ON DUPLICATE KEY UPDATE 確保無重複資料。")
    else:
        print("\n取消寫入。")

if __name__ == "__main__":
    main()
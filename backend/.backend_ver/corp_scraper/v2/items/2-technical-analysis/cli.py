# ./ip_dc_all.sh
# ./enter_dc.sh
#
# fin_django_db
# mariadb -u root -p
#
# fin_django_backend
# cd .backend_ver/corp_scraper/v2/items/2-technical-analysis
# python cli.py
#
# python /app/.backend_ver/corp_scraper/v2/items/2-technical-analysis/cli.py
#
# cli.py
import sys
from ta_analyzer import TAAnalyzer
from db_handler import DBHandler
import twstock
from dotenv import load_dotenv
import os

load_dotenv(".env")

def get_period_input():
    print("\n請選擇欲寫入資料庫的資料時間範圍：")
    print("1. 1週 (1wk)")
    print("2. 1個月 (1mo)")
    print("3. 1季 (3mo)")
    print("4. 1年 (1y)")
    
    mapping = {'1': '1wk', '2': '1mo', '3': '3mo', '4': '1y'}
    choice = input("請輸入選項 (1-4) [預設: 2]: ").strip()
    return mapping.get(choice, '1mo')

def main():
    print("=== Yahoo 股市風格：技術分析資料(TA) 擷取系統 ===")
    
    analyzer = TAAnalyzer()
    db = DBHandler(host='172.18.0.4', user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), db='stock_db') # 記得確認 db_handler.py 內的密碼設定正確

    while True:
        stock_id = input("\n請輸入台股代碼 (輸入 'q' 退出): ").strip()
        if stock_id.lower() == 'q':
            break

        if stock_id not in twstock.codes:
            print(f"[提示] 代碼 {stock_id} 不在內建列表，將直接呼叫 yfinance 嘗試。")

        # 1. 抓取與翻譯公司資訊
        print("\n[系統] 正在獲取並翻譯公司簡介...")
        name, summary = analyzer.fetch_company_info(stock_id)
        
        print(f"\n--- {name} ({stock_id}) ---")
        print(f"【中文簡介】:\n{summary}\n")

        # 2. 確認是否繼續
        if input("請問是否繼續抓取該公司的技術分析資料？(y/n): ").lower() != 'y':
            print("已取消操作。")
            continue

        # 3. 選擇時間範圍
        period_str = get_period_input()

        # 4. 抓取並計算資料
        print(f"\n[系統] 正在抓取歷史股價，並計算擷取 {period_str} 範圍的技術指標...")
        df_ta = analyzer.calculate_ta(stock_id, period_str)
        
        if df_ta is None or df_ta.empty:
            print("[錯誤] 無法抓取到有效股價，取消寫入。")
            continue

        # 顯示預覽
        print(f"\n=== 取回共 {len(df_ta)} 筆資料，最新 3 筆預覽 ===")
        preview_cols = ['Date', 'Close', 'Volume', 'K', 'D', 'MACD', 'BIAS', 'CDP']
        print(df_ta[preview_cols].tail(3).to_string(index=False))

        # 5. 寫入資料庫
        print("\n[系統] 準備將資料寫入 MariaDB ...")
        success, message = db.save_ta_data(stock_id, df_ta)
        
        if success:
            print(f"✅ [成功] {message}")
        else:
            print(f"❌ [失敗] {message}")

if __name__ == "__main__":
    main()
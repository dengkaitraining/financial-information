# ./ip_dc_all.sh
# ./enter_dc.sh
#
# fin_django_db
# mariadb -u root -p
#
# fin_django_backend
# cd .backend_ver/corp_scraper/v2/items/1-profile
# python cli.py
#
# python /app/.backend_ver/corp_scraper/v2/items/1-profile/cli.py
#
# cli.py
import sys
import pprint
from fetcher import StockProfileFetcher
from db import DatabaseManager
from dotenv import load_dotenv
import os

load_dotenv(".env")

def main():
    print("=" * 65)
    print("      台股公司基本資料 (Yahoo股市風格) 抓取與 MariaDB 寫入測試系統")
    print("=" * 65)

    # 1. 初始化元件
    fetcher = StockProfileFetcher()
    
    # 請在此處調整您的 MariaDB 資料庫連線設定
    db = DatabaseManager(
        host='172.18.0.4',
        port=3306,
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        db='stock_db'
    )

    while True:
        symbol = input("\n[?] 請輸入要查詢的台灣股票代碼 (輸入 Q 離開): ").strip()
        if symbol.upper() == 'Q':
            print("系統已結束作業。")
            break

        if not symbol.isdigit():
            print("[-] 錯誤：股票代碼必須為數字，請重新輸入。")
            continue

        print(f"\n[*] 正在搜尋並擷取 {symbol} 的公司基本資料、行事曆與新聞/公告...")
        
        # 擷取 basic profile
        profile = fetcher.fetch_profile(symbol)
        
        # 擷取 calendar
        calendar = fetcher.fetch_calendar(symbol)
        
        # 擷取 news & announcements
        company_name = profile.get('company_name', symbol)
        news, announcements = fetcher.fetch_news_and_announcements(symbol, company_name)

        # 顯示擷取結果供使用者確認
        print("\n" + "="*20 + " 1. 公司基本資料 (Profile) " + "="*20)
        for k, v in profile.items():
            print(f"  {k:22s}: {v}")

        print("\n" + "="*20 + " 2. 行事曆 (Calendar) " + "="*20)
        if calendar:
            for idx, cal in enumerate(calendar, 1):
                print(f"  [{idx}] {cal['event_type']} | 日期: {cal['event_date']} | 說明: {cal['description']}")
        else:
            print("  (未擷取到相關行事曆事件)")

        print("\n" + "="*20 + " 3. 新聞與個股公告概要 " + "="*20)
        print(f"  - 相關新聞筆數: {len(news)} 筆")
        print(f"  - 個股公告筆數: {len(announcements)} 筆")
        if news:
            print(f"  [最新新聞範例] {news[0]['title']} ({news[0]['publisher']})")
        if announcements:
            print(f"  [最新公告範例] {announcements[0]['title']} ({announcements[0]['publisher']})")

        # 2. 使用者確認步驟
        print("\n" + "-" * 65)
        confirm = input(f"[?] 請確認是否將以上 {symbol} 資料寫入 MariaDB 12.3 資料庫？ (Y/N): ").strip().upper()
        
        if confirm == 'Y':
            print("\n[*] 開始執行資料庫寫入 (使用 ON DUPLICATE KEY UPDATE 確保無重複數據)...")
            
            try:
                # 寫入 Profile
                if profile:
                    db.upsert_profile(profile)
                    print("  [+] 公司基本資料已成功寫入/更新。")
                else:
                    print("  [-] 未抓取到基本資料，跳過寫入。")

                # 寫入 Calendar
                if calendar:
                    cal_count = db.upsert_calendars(calendar)
                    print(f"  [+] 行事曆資料已成功寫入/更新 {cal_count} 筆。")
                else:
                    print("  [-] 未抓取到行事曆資料，跳過寫入。")

                # 寫入 News & Announcements
                all_news = news + announcements
                if all_news:
                    news_count = db.upsert_news(all_news)
                    print(f"  [+] 新聞與個股公告已成功寫入/更新 {news_count} 筆。")
                else:
                    print("  [-] 未抓取到新聞/公告資料，跳過寫入。")

                print("\n[✓] 完成！所有數據已更新至 MariaDB。")

            except Exception as e:
                print(f"\n[!] 資料庫寫入失敗，原因: {e}")
        else:
            print("[-] 使用者取消寫入，資料未變更。")

if __name__ == '__main__':
    main()
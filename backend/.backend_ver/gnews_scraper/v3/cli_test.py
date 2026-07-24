from gnews_crawler import GoogleNewsCrawler
from dotenv import load_dotenv
import os

load_dotenv(".env")

# 請依據您的 MariaDB 環境修改以下設定
DB_CONFIG = {
    "user": os.getenv("DB_USER"),          # 資料庫帳號
    "password": os.getenv("DB_PASSWORD"),  # 資料庫密碼
    "host": "172.18.0.3",
    "port": 3306,
    "database": "tw_stock_analysis"   # 請確保此資料庫已事先建立 (CREATE DATABASE gnews_db;)
}

def main():
    print("=== Google 新聞爬蟲測試系統 ===")
    
    # 1. 實例化爬蟲物件
    crawler = GoogleNewsCrawler(db_config=DB_CONFIG)

    try:
        # 2. 自動建表
        crawler.setup_database()

        # 3. 將初始參數寫入資料表 (依照 Spec 2 的設定)
        crawler.init_parameters(lang='zh-TW', country='TW', period='4h', max_results=100)

        # 4. 從資料庫讀取參數並初始化 GNews 物件
        crawler.load_parameters_and_init_gnews()

        # 5. 執行爬蟲抓取資料 (此處可輸入關鍵字，留白則抓取頭條)
        keyword = input("\n請輸入要搜尋的新聞關鍵字 (直接按 Enter 抓取即時頭條): ").strip()
        news_results = crawler.fetch_news(keyword=keyword if keyword else None)

        # 顯示抓取結果摘要供使用者確認
        print(f"\n共抓取到 {len(news_results)} 筆新聞。前 3 筆預覽：")
        for i, article in enumerate(news_results[:3], 1):
            pub_name = article.get('publisher', {}).get('title', '未知來源')
            print(f"[{i}] {article.get('title')}")
            print(f"    來源: {pub_name} | 時間: {article.get('published date')}")

        if not news_results:
            print("查無新聞，程式結束。")
            return

        # 6. 使用者確認機制
        confirm = input(f"\n請問是否確認將這 {len(news_results)} 筆新聞寫入 MariaDB 資料庫？ (y/n): ").strip().lower()
        
        if confirm == 'y':
            crawler.save_news_to_db(news_results)
        else:
            print("[系統] 取消寫入，資料已捨棄。")

    finally:
        # 確保資料庫連線關閉
        crawler.close()
        print("=== 測試結束 ===")

if __name__ == "__main__":
    main()
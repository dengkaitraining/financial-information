# ./ip_dc_all.sh
# ./enter_dc.sh
#
# fin_django_db
# mariadb -u root -p
#
# fin_django_backend
# cd .backend_ver/corp_scraper/v2/items/1-profile
# python main_cli.py
#
# python /app/.backend_ver/corp_scraper/v2/items/1-profile/main_cli.py
#
# main_cli.py
import sys
from stock_profile import StockProfileFetcher, DatabaseManager
from dotenv import load_dotenv
import os

load_dotenv(".env")

# MariaDB 資料庫連線配置
DB_CONFIG = {
    "host": "172.18.0.4",
    "port": 3306,
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),  # 請替換為您的 DB 密碼
    'database': 'tw_stock_db',
    'charset': 'utf8mb4'
}

def print_summary(data: dict):
    """預覽擷取到的資料內容"""
    profile = data.get('profile', {})
    calendar = data.get('calendar', [])
    news = data.get('news', [])

    print("\n================== [1. 公司基本資料預覽] ==================")
    print(f"股票代碼: {profile.get('stock_id')} | 公司名稱: {profile.get('name')}")
    print(f"產業類別: {profile.get('industry')} | 市場別: {profile.get('market_type')}")
    print(f"市值 (百萬): {profile.get('market_cap')} | 已發行股數: {profile.get('issued_shares')}")
    print(f"電話: {profile.get('phone')} | 網站: {profile.get('website')}")
    print(f"主營業務 (已翻譯): {profile.get('main_business')[:80] if profile.get('main_business') else '無'}...")

    print("\n================== [2. 行事曆資料預覽] ==================")
    if calendar:
        for cal in calendar:
            print(f"年度: {cal.get('year')} | 股東常會: {cal.get('agm_date')} | 現金股利發放日: {cal.get('cash_div_date')}")
    else:
        print("尚無行事曆資料。")

    print(f"\n================== [3. 新聞與公告預覽 (共 {len(news)} 筆)] ==================")
    if news:
        for idx, item in enumerate(news[:5], 1):  # 預覽前 5 筆新聞
            print(f"[{idx}] [{item.get('category')}] {item.get('title')}")
            print(f"    來源: {item.get('source')} | 時間: {item.get('published_at') or '未提供'}")
    else:
        print("尚無新聞資料。")
    print("=========================================================\n")


def main():
    db_mgr = DatabaseManager(DB_CONFIG)

    while True:
        print("\n*** 台股公司 Profile 與 Google News 整合 CLI 測試 ***")
        stock_id = input("請輸入股票代碼 (輸入 'q' 退出): ").strip()

        if stock_id.lower() == 'q':
            print("退出程式。")
            sys.exit(0)

        if not stock_id:
            print("請輸入有效的股票代碼！")
            continue

        try:
            fetcher = StockProfileFetcher(stock_id)
            fetched_data = fetcher.fetch_all()

            print_summary(fetched_data)

            confirm = input("確認將上述資料寫入 MariaDB 資料庫？ (y/N): ").strip().lower()

            if confirm == 'y':
                db_mgr.upsert_data(fetched_data)
            else:
                print("操作已取消，資料未寫入。")

        except Exception as e:
            print(f"執行過程中發生錯誤: {e}")


if __name__ == '__main__':
    main()
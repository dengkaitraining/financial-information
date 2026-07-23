import sys
import time
import logging
import pandas as pd
import config
from news_scraper import GoogleNewsScraper

class GNewsCLI:
    """處理 Console 互動輸入、雙向日誌輸出與 CSV 檔案儲存的類別"""

    def __init__(self):
        # 建立必要目錄
        config.NEWS_DIR.mkdir(parents=True, exist_ok=True)
        config.LOGS_DIR.mkdir(parents=True, exist_ok=True)

        # 產生單次運行的 Timestamp 標籤
        self.timestamp_str = str(int(time.time() * 1000))
        
        # 初始化 Logging
        self._setup_logging()

    def _setup_logging(self):
        """設置日誌：同時紀錄至控制台與 txt 檔案"""
        log_file = config.LOGS_DIR / f"log_{self.timestamp_str}.txt"
        
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.handlers.clear()

        formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        # Console 輸出
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File TXT 輸出
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logging.info(f"Log 日誌檔案已初始化，檔名: log_{self.timestamp_str}.txt")

    def prompt_period(self) -> str:
        """引導使用者輸入 period"""
        print("\n" + "=" * 55)
        print("【步驟 1/2】設定抓取時間區間 (Period)")
        print("格式提示: 1h (1小時), 4h (4小時), 1d (1天), 7d (7天)")
        print("=" * 55)
        
        period = input(f"請輸入時間範圍 (直接 Enter 預設為 {config.DEFAULT_PERIOD}): ").strip()
        if not period:
            period = config.DEFAULT_PERIOD
            logging.info(f"使用預設時間區間: {period}")
        else:
            logging.info(f"使用者輸入時間區間: {period}")
        return period

    def prompt_keywords(self) -> list[str]:
        """引導使用者輸入關鍵字 (最多 4 個)"""
        print("\n" + "=" * 55)
        print("【步驟 2/2】設定關鍵字 (至多 4 個)")
        print("格式提示: 請以逗號隔開關鍵字 (全形/半形皆可)")
        print("範例: 人工智慧, RAG 檢索增強, 大型語言模型, LLM")
        print("=" * 55)

        while True:
            raw_input = input("請輸入關鍵字: ").strip()
            if not raw_input:
                print("[!] 關鍵字不能為空，請重新輸入。")
                continue

            # 替換全形逗號並拆分
            kw_list = [k.strip() for k in raw_input.replace("，", ",").split(",") if k.strip()]

            if not kw_list:
                print("[!] 未偵測到有效關鍵字，請重新輸入。")
                continue

            if len(kw_list) > config.MAX_KEYWORDS_LIMIT:
                print(f"[!] 警告：關鍵字數量超過上限 ({config.MAX_KEYWORDS_LIMIT}個)，系統將自動截取前 {config.MAX_KEYWORDS_LIMIT} 個。")
                kw_list = kw_list[:config.MAX_KEYWORDS_LIMIT]

            logging.info(f"最終採用的關鍵字陣列: {kw_list}")
            return kw_list

    def save_csv(self, news_data: list[dict]):
        """將新聞資料儲存為 CSV"""
        csv_filename = config.NEWS_DIR / f"google_news_data_{self.timestamp_str}.csv"
        df = pd.DataFrame(news_data)

        if not df.empty:
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            logging.info(f"資料成功匯出至 CSV！檔案名稱: google_news_data_{self.timestamp_str}.csv")
        else:
            logging.warning("未抓取到任何新聞，本次執行不儲存 CSV。")

    def run(self):
        """CLI 主邏輯流程"""
        logging.info("=== GNews CLI 應用程式啟動 ===")
        
        period = self.prompt_period()
        keywords = self.prompt_keywords()

        # 呼叫爬蟲核心服務
        scraper = GoogleNewsScraper(period=period)
        results = scraper.fetch_news(keywords)

        # 寫入檔案
        self.save_csv(results)
        logging.info("=== 作業完成，程式關閉 ===")
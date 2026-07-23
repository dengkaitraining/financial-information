import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from gnews import GNews
import config

class GoogleNewsScraper:
    """負責 Google 新聞爬取與資料格式化的核心類別"""

    def __init__(
        self, 
        period: str = config.DEFAULT_PERIOD, 
        language: str = config.DEFAULT_LANGUAGE, 
        country: str = config.DEFAULT_COUNTRY, 
        max_results: int = config.DEFAULT_MAX_RESULTS
    ):
        self.period = period
        self.language = language
        self.country = country
        self.max_results = max_results
        
        # 初始化 GNews 套件
        self.gnews = GNews(
            language=self.language,
            country=self.country,
            period=self.period,
            max_results=self.max_results
        )

    def fetch_news(self, keywords: list[str]) -> list[dict]:
        """
        根據關鍵字列表爬取新聞並完成清洗整理
        """
        combined_keywords = " OR ".join(keywords)
        logging.info(f"開始抓取關鍵字：[{combined_keywords}] 的最新新聞 (時間區間: {self.period})...")

        try:
            news_results = self.gnews.get_news(combined_keywords)
        except Exception as e:
            logging.error(f"連線或爬取新聞時發生例外錯誤: {e}")
            return []

        news_list = []
        fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for item in news_results:
            try:
                pub_date_str = item.get('published date')
                if not pub_date_str:
                    continue

                # 轉成 UTC 並轉換至 Asia/Taipei 時區
                n_time_utc = datetime.strptime(pub_date_str, "%a, %d %b %Y %H:%M:%S GMT").replace(tzinfo=timezone.utc)
                n_time = n_time_utc.astimezone(ZoneInfo("Asia/Taipei")).timestamp()

                new_item = {
                    "index": int(n_time * 1000),
                    "from": "Google New",
                    "title": str(item.get('title')),
                    "timestamp": int(n_time),
                    "datetime": str(datetime.fromtimestamp(n_time).strftime("%Y-%m-%d %H:%M:%S, %a")),
                    "source": str(item.get('publisher', {}).get('title', '')),
                    "url": str(item.get('url')),
                    "description": str(item.get('description')),
                    "userid": "sys",
                    "m_date": str(fetch_time)
                }
                news_list.append(new_item)

            except Exception as parse_err:
                logging.warning(f"單筆資料解析失敗，已略過: {parse_err}")
                continue

        # 按時間戳記升冪排序
        news_list.sort(key=lambda x: x['timestamp'], reverse=False)
        logging.info(f"成功處理 {len(news_list)} 筆新聞資料。")
        return news_list
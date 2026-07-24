import mariadb
import sys
from gnews import GNews

class GoogleNewsCrawler:
    def __init__(self, db_config):
        """
        初始化資料庫連線
        """
        self.db_config = db_config
        self.conn = self._connect_db()
        self.gnews_client = None

    def _connect_db(self):
        try:
            conn = mariadb.connect(**self.db_config)
            return conn
        except mariadb.Error as e:
            print(f"[錯誤] 無法連線至 MariaDB: {e}")
            sys.exit(1)

    def setup_database(self):
        """
        建立所需的資料表 (若尚未建立)
        """
        cursor = self.conn.cursor()
        
        # 建立參數表
        cursor.execute("""
CREATE TABLE IF NOT EXISTS `parameter_settings` (
    `id` INT AUTO_INCREMENT COMMENT '主鍵',
    `language` VARCHAR(10) NOT NULL COMMENT '語系地區',
    `country` VARCHAR(10) NOT NULL COMMENT '地區',
    `period` VARCHAR(10) NOT NULL COMMENT '過去區間的新聞',
    `max_results` INT NOT NULL COMMENT '單次抓取量',
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT '參數設定表單 (Parameter Settings Table)';
        """)
        
        # 建立新聞資料表
        cursor.execute("""
CREATE TABLE IF NOT EXISTS `news_data` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT COMMENT '主鍵',
    `title` TEXT NOT NULL COMMENT '新聞標題',
    `published_date` VARCHAR(100) COMMENT '發布時間',
    `publisher` VARCHAR(100) COMMENT '新聞來源',
    `url` TEXT NOT NULL COMMENT '文章連結',
    `description` TEXT COMMENT '說明摘要',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `unique_url` (`url`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT '建立新聞資料表單 (News Data Table)';
        """)
        self.conn.commit()
        cursor.close()

    def init_parameters(self, lang='zh-TW', country='TW', period='4h', max_results=100):
        """
        將預設參數寫入資料庫。為了簡化，若表內無資料則新增，有資料則更新第一筆。
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM parameter_settings LIMIT 1")
        row = cursor.fetchone()

        if row:
            cursor.execute("""
                UPDATE parameter_settings 
                SET language=?, country=?, period=?, max_results=? 
                WHERE id=?
            """, (lang, country, period, max_results, row[0]))
        else:
            cursor.execute("""
                INSERT INTO parameter_settings (language, country, period, max_results) 
                VALUES (?, ?, ?, ?)
            """, (lang, country, period, max_results))
        
        self.conn.commit()
        cursor.close()
        print("[系統] 參數已成功寫入資料庫。")

    def load_parameters_and_init_gnews(self):
        """
        從資料庫讀取參數，並以此初始化 GNews 物件
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT language, country, period, max_results FROM parameter_settings LIMIT 1")
        row = cursor.fetchone()
        cursor.close()

        if not row:
            raise ValueError("資料庫中無設定參數，請先執行 init_parameters()")

        lang, country, period, max_results = row
        print(f"[系統] 載入設定參數: 語系={lang}, 地區={country}, 期間={period}, 最大數量={max_results}")
        
        # 使用資料庫讀出的參數初始化 GNews
        self.gnews_client = GNews(
            language=lang, 
            country=country, 
            period=period, 
            max_results=max_results
        )

    def fetch_news(self, keyword=None):
        """
        抓取新聞，可指定關鍵字。若無指定則抓取焦點新聞。
        """
        if not self.gnews_client:
            raise RuntimeError("GNews 尚未初始化，請先呼叫 load_parameters_and_init_gnews()")

        print(f"[系統] 開始抓取新聞...")
        if keyword:
            news_list = self.gnews_client.get_news(keyword)
        else:
            news_list = self.gnews_client.get_top_news()
            
        return news_list

    def save_news_to_db(self, news_list):
        """
        將確認後的新聞清單寫入資料庫，並過濾重複的新聞（依據 URL）
        """
        if not news_list:
            print("[系統] 沒有新聞可供儲存。")
            return

        cursor = self.conn.cursor()
        
        # 用來檢查是否已存在的 SQL
        check_query = "SELECT COUNT(*) FROM news_data WHERE url = ?"
        # 用來新增資料的 SQL
        insert_query = """
            INSERT INTO news_data (title, published_date, publisher, url, description)
            VALUES (?, ?, ?, ?, ?)
        """
        
        saved_count = 0
        duplicate_count = 0
        
        for news in news_list:
            url = news.get('url', '')
            
            # 1. 檢查該 URL 是否已經存在於資料庫中
            cursor.execute(check_query, (url,))
            exists = cursor.fetchone()[0]
            
            if exists > 0:
                # 發現重複，跳過此筆紀錄
                duplicate_count += 1
                continue

            # 2. 若無重複，則提取其他欄位並寫入
            title = news.get('title', '')
            pub_date = news.get('published date', '')
            
            # GNews 的 publisher 是一個字典: {'href': '...', 'title': '新聞來源'}
            publisher_raw = news.get('publisher', {})
            publisher = publisher_raw.get('title', str(publisher_raw)) if isinstance(publisher_raw, dict) else str(publisher_raw)
            description = news.get('description', '')

            try:
                cursor.execute(insert_query, (title, pub_date, publisher, url, description))
                saved_count += 1
            except mariadb.Error as e:
                print(f"[警告] 儲存新聞「{title[:10]}...」時發生錯誤: {e}")

        self.conn.commit()
        cursor.close()
        
        # 顯示最終寫入與過濾的統計數據
        print(f"[系統] 執行完畢！成功寫入 {saved_count} 筆新資料，過濾掉 {duplicate_count} 筆重複資料。")

    def close(self):
        if self.conn:
            self.conn.close()
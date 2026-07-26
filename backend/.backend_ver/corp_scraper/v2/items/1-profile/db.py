# db.py
import MySQLdb
import MySQLdb.cursors
from typing import Dict, List
import logging

class DatabaseManager:
    def __init__(self, host='localhost', port=3306, user='root', password='', db='stock_db'):
        # MySQLdb (mysqlclient) 的設定參數
        self.config = {
            'host': host,
            'port': port,
            'user': user,
            'passwd': password,  # 注意：mysqlclient 參數名稱為 passwd
            'db': db,
            'charset': 'utf8mb4',
            'autocommit': True,
            'cursorclass': MySQLdb.cursors.DictCursor
        }

    def get_connection(self):
        return MySQLdb.connect(**self.config)

    def upsert_profile(self, profile: Dict) -> bool:
        """寫入或更新公司基本資料 (ON DUPLICATE KEY UPDATE)"""
        if not profile or not profile.get('symbol'):
            logging.info("No profile data to write.")
            return False

        sql = """
        INSERT INTO company_profile (
            symbol, tax_id, company_name, spokesperson, eng_short_name, deputy_spokesperson,
            establishment_date, phone, listing_date, fax, industry_category, website,
            chairman, email, general_manager, stock_transfer_agent, capital, auditor,
            issued_shares, address, market_cap_millions, market_type, insider_holding_ratio,
            group_name, main_business
        ) VALUES (
            %(symbol)s, %(tax_id)s, %(company_name)s, %(spokesperson)s, %(eng_short_name)s, %(deputy_spokesperson)s,
            %(establishment_date)s, %(phone)s, %(listing_date)s, %(fax)s, %(industry_category)s, %(website)s,
            %(chairman)s, %(email)s, %(general_manager)s, %(stock_transfer_agent)s, %(capital)s, %(auditor)s,
            %(issued_shares)s, %(address)s, %(market_cap_millions)s, %(market_type)s, %(insider_holding_ratio)s,
            %(group_name)s, %(main_business)s
        )
        ON DUPLICATE KEY UPDATE
            company_name = VALUES(company_name),
            eng_short_name = VALUES(eng_short_name),
            phone = VALUES(phone),
            industry_category = VALUES(industry_category),
            website = VALUES(website),
            chairman = VALUES(chairman),
            general_manager = VALUES(general_manager),
            issued_shares = VALUES(issued_shares),
            address = VALUES(address),
            market_cap_millions = VALUES(market_cap_millions),
            market_type = VALUES(market_type),
            insider_holding_ratio = VALUES(insider_holding_ratio),
            group_name = VALUES(group_name),
            main_business = VALUES(main_business);
        """
        
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, profile)
        finally:
            conn.close() # 確保連線被關閉
            
        return True

    def upsert_calendars(self, calendar_list: List[Dict]) -> int:
        """批次寫入或更新公司行事曆資料"""
        if not calendar_list:
            logging.info("No calendar data to write.")
            return 0

        sql = """
        INSERT INTO company_calendar (symbol, event_type, event_date, description)
        VALUES (%(symbol)s, %(event_type)s, %(event_date)s, %(description)s)
        ON DUPLICATE KEY UPDATE
            description = VALUES(description);
        """
        written_count = 0
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                for item in calendar_list:
                    cursor.execute(sql, item)
                    written_count += 1
        finally:
            conn.close()
            
        return written_count

    def upsert_news(self, news_list: List[Dict]) -> int:
        """批次寫入或更新新聞與公告 (基於 symbol + url 防重複)"""
        if not news_list:
            logging.info("No news data to write.")
            return 0

        sql = """
        INSERT INTO company_news (symbol, news_type, title, url, publisher, published_date, summary)
        VALUES (%(symbol)s, %(news_type)s, %(title)s, %(url)s, %(publisher)s, %(published_date)s, %(summary)s)
        ON DUPLICATE KEY UPDATE
            title = VALUES(title),
            publisher = VALUES(publisher),
            summary = VALUES(summary);
        """
        written_count = 0
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                for item in news_list:
                    pub_date = item.get('published_date')
                    if pub_date and not isinstance(pub_date, str):
                        item['published_date'] = str(pub_date)
                    try:
                        cursor.execute(sql, item)
                        written_count += 1
                    except Exception as e:
                        logging.warning(f"Failed to insert news item: {item.get('url')} - {e}")
        finally:
            conn.close()
            
        return written_count
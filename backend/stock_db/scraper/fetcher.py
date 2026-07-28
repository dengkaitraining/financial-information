# ==============================================================================
# 台股公司基本資料與新聞公告爬蟲 (backend/stock_db/scraper/fetcher.py)
# 說明：已搬移至 stock_db 並支援 UTC+8 台北時間解析
# ==============================================================================

import datetime
import logging
import zoneinfo
from typing import Dict, List, Tuple
from email.utils import parsedate_to_datetime
import twstock
import yfinance as yf
from gnews import GNews
from .translator import TextTranslator

class StockProfileFetcher:
    def __init__(self):
        self.translator = TextTranslator()
        # 初始化 GNews (針對繁體中文/台灣地區)
        self.gn = GNews(language='zh-TW', country='TW', max_results=100)

    def _parse_gnews_date(self, date_str: str) -> str:
        """將 GNews 的時間字串轉換為 MariaDB DATETIME 格式 (轉換為 UTC+8 台灣時間)"""
        if not date_str:
            return None
        try:
            # 將 'Thu, 15 Aug 2024 07:00:00 GMT' 轉換為 datetime 物件
            dt_obj = parsedate_to_datetime(date_str)
            # 轉換為台北時區 (UTC+8)
            dt_taipei = dt_obj.astimezone(zoneinfo.ZoneInfo('Asia/Taipei'))
            # 格式化為資料庫支援的格式
            return dt_taipei.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            logging.warning(f"Date parse error for '{date_str}': {e}")
            return None

    def _get_ticker_stock_id(self, stock_id: str) -> Tuple[str, str]:
        """判斷市場類型並回傳 yfinance 格式的股票代碼 (e.g., 2330.TW or 6488.TWO)"""
        if stock_id in twstock.codes:
            info = twstock.codes[stock_id]
            market = info.market
            if market == '上市':
                return f"{stock_id}.TW", "上市"
            elif market in ['上櫃', '興櫃']:
                return f"{stock_id}.TWO", market
        return f"{stock_id}.TW", "上市"

    def fetch_profile(self, stock_id: str) -> Dict:
        """擷取公司基本資料 25 項欄位"""
        yf_stock_id, market_type = self._get_ticker_stock_id(stock_id)
        ticker = yf.Ticker(yf_stock_id)
        info = ticker.info or {}
        tw_info = twstock.codes.get(stock_id, None)

        # 董事長與總經理資訊 (嘗試從 yfinance officers 取得)
        chairman = None
        general_manager = None
        for officer in info.get('companyOfficers', []):
            title = officer.get('title', '').lower()
            name = officer.get('name', '')
            if 'chairman' in title or '董事長' in title:
                chairman = chairman or name
            if 'ceo' in title or 'chief executive' in title or '總經理' in title:
                general_manager = general_manager or name

        # 市值計算 (百萬)
        market_cap = info.get('marketCap')
        market_cap_m = round(market_cap / 1_000_000, 2) if market_cap else None

        # 主要業務 (英文自動翻譯成繁體中文)
        business_summary = info.get('longBusinessSummary', '')
        if business_summary:
            business_summary = self.translator.translate(business_summary)

        # 計算股本 (台股每股面額 10 元，股本 = 流通股數 * 10)
        # 若為美股，通常直接看流通股數或總市值，一般不特別計算台制「股本」
        shares = info.get('sharesOutstanding')
        tw_capital = round(float(shares) * 10, 2) if (shares is not None and (".TW" in yf_stock_id or ".TWO" in yf_stock_id)) else None

        # 安全地讀取 'founded' 欄位，若不存在則回傳 None
        founded_date = info.get("founded", None)

        profile = {
            'stock_id': stock_id,
            'tax_id': None,  # MOPS/公開資訊觀測站可補充，預設為 None
            'company_name': tw_info.name if tw_info else info.get('shortName', stock_id),
            'spokesperson': None,
            'eng_short_name': info.get('shortName'),
            'deputy_spokesperson': None,
            'establishment_date': founded_date,
            'phone': info.get('phone'),
            'listing_date': tw_info.start if tw_info else None,
            'fax': info.get('fax'),
            'industry_category': tw_info.group if tw_info else info.get('industry'),
            'website': info.get('website'),
            'chairman': chairman,
            'email': None,
            'general_manager': general_manager,
            'stock_transfer_agent': None,
            'capital': tw_capital,
            'auditor': None,
            'issued_shares': info.get('sharesOutstanding'),
            'address': f"{info.get('address1', '')} {info.get('city', '')} {info.get('country', '')}".strip() or None,
            'market_cap_millions': market_cap_m,
            'market_type': market_type,
            'insider_holding_ratio': round(info.get('heldPercentInsiders', 0) * 100, 2) if info.get('heldPercentInsiders') else None,
            'group_name': tw_info.group if tw_info else None,
            'main_business': business_summary or None
        }
        return profile

    def fetch_calendar(self, stock_id: str) -> List[Dict]:
        """擷取行事曆：股東常會、配股發放日、現金股利發放日"""
        yf_stock_id, _ = self._get_ticker_stock_id(stock_id)
        ticker = yf.Ticker(yf_stock_id)
        calendar_events = []

        try:
            cal = ticker.calendar
            if isinstance(cal, dict):
                # 股東常會 / Dividend Events
                dividend_date = cal.get('Dividend Date')
                ex_div_date = cal.get('Ex-Dividend Date')
                
                if dividend_date:
                    d_date = dividend_date if isinstance(dividend_date, datetime.date) else dividend_date[0]
                    calendar_events.append({
                        'stock_id': stock_id,
                        'event_type': '現金股利發放日',
                        'event_date': str(d_date),
                        'description': '現金股利發放'
                    })
                if ex_div_date:
                    e_date = ex_div_date if isinstance(ex_div_date, datetime.date) else ex_div_date[0]
                    calendar_events.append({
                        'stock_id': stock_id,
                        'event_type': '配股發放日',
                        'event_date': str(e_date),
                        'description': '除權息發放日/除權日'
                    })
        except Exception as e:
            logging.error(f"Error fetching calendar for {stock_id}: {e}")

        return calendar_events

    def fetch_news_and_announcements(self, stock_id: str, company_name: str) -> Tuple[List[Dict], List[Dict]]:
        """擷取近 100 筆相關新聞與近 100 筆個股公告"""
        # 1. 抓取相關新聞
        news_query = f"{stock_id} {company_name}"
        raw_news = self.gn.get_news(news_query) or []
        news_list = []

        for item in raw_news[:100]:
            title = item.get('title', '')
            desc = item.get('description', '')
            
            pub_date = self._parse_gnews_date(item.get('published date'))
            
            news_list.append({
                'stock_id': stock_id,
                'news_type': 'NEWS',
                'title': title,
                'url': item.get('url'),
                'publisher': item.get('publisher', {}).get('title', 'GNews'),
                'published_date': pub_date,
                'summary': desc
            })

        # 2. 抓取個股公告
        ann_query = f"{stock_id} {company_name} 重訊 公告"
        raw_ann = self.gn.get_news(ann_query) or []
        ann_list = []

        for item in raw_ann[:100]:
            title = item.get('title', '')
            desc = item.get('description', '')
            
            pub_date = self._parse_gnews_date(item.get('published date'))
            
            ann_list.append({
                'stock_id': stock_id,
                'news_type': 'ANNOUNCEMENT',
                'title': title,
                'url': item.get('url'),
                'publisher': item.get('publisher', {}).get('title', '公開資訊/媒體'),
                'published_date': pub_date,
                'summary': desc
            })

        return news_list, ann_list

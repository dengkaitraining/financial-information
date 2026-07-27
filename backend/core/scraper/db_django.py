# ==============================================================================
# 使用 Django ORM 寫入與更新資料 (backend/core/scraper/db_django.py)
# 說明：以 Django ORM update_or_create 機制實作，防止資料重複寫入，適配多資料庫路由
# ==============================================================================

import logging
from typing import Dict, List
from core.models import CompanyProfile, CompanyCalendar, CompanyNews

logger = logging.getLogger(__name__)

class DjangoDatabaseManager:
    def upsert_profile(self, profile: Dict) -> bool:
        """寫入或更新公司基本資料 (使用 Django ORM)"""
        if not profile or not profile.get('stock_id'):
            logger.info("No profile data to write.")
            return False

        # 將 dict 複製一份，避免 mutate 原資料
        data = profile.copy()
        stock_id = data.pop('stock_id')

        # 清洗 Date 欄位格式 (將 YYYY/MM/DD 置換為 YYYY-MM-DD)
        for field in ['establishment_date', 'listing_date']:
            val = data.get(field)
            if val and isinstance(val, str):
                data[field] = val.replace('/', '-')

        try:
            CompanyProfile.objects.update_or_create(
                stock_id=stock_id,
                defaults=data
            )
            return True
        except Exception as e:
            logger.error(f"Failed to upsert profile for {stock_id}: {e}")
            raise e

    def upsert_calendars(self, calendar_list: List[Dict]) -> int:
        """批次寫入或更新公司行事曆資料"""
        if not calendar_list:
            logger.info("No calendar data to write.")
            return 0

        written_count = 0
        for item in calendar_list:
            try:
                stock_id = item.get('stock_id')
                # 確保主表有這筆股票，不然外鍵會失敗
                stock = CompanyProfile.objects.get(stock_id=stock_id)
                event_type = item.get('event_type')
                event_date = item.get('event_date')
                description = item.get('description')

                CompanyCalendar.objects.update_or_create(
                    stock=stock,
                    event_type=event_type,
                    event_date=event_date,
                    defaults={'description': description}
                )
                written_count += 1
            except CompanyProfile.DoesNotExist:
                logger.warning(f"Skipping calendar item, CompanyProfile for {stock_id} does not exist.")
            except Exception as e:
                logger.warning(f"Failed to upsert calendar item: {item} - {e}")
        return written_count

    def upsert_news(self, news_list: List[Dict]) -> int:
        """批次寫入或更新新聞與公告 (基於 stock_id + url 防重複)"""
        if not news_list:
            logger.info("No news data to write.")
            return 0

        written_count = 0
        for item in news_list:
            stock_id = item.get('stock_id')
            url = item.get('url')
            # 截斷過長的 url 以防長度超出 CharField 限制
            if url and len(url) > 500:
                url = url[:500]

            try:
                stock = CompanyProfile.objects.get(stock_id=stock_id)
                news_type = item.get('news_type')
                title = item.get('title')
                publisher = item.get('publisher')
                published_date = item.get('published_date')
                summary = item.get('summary')

                CompanyNews.objects.update_or_create(
                    stock=stock,
                    url=url,
                    defaults={
                        'news_type': news_type,
                        'title': title,
                        'publisher': publisher,
                        'published_date': published_date,
                        'summary': summary
                    }
                )
                written_count += 1
            except CompanyProfile.DoesNotExist:
                logger.warning(f"Skipping news item, CompanyProfile for {stock_id} does not exist.")
            except Exception as e:
                logger.warning(f"Failed to upsert news item for url {url}: {e}")
        return written_count

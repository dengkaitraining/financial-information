# ==============================================================================
# 使用 Django ORM 寫入與更新資料 (backend/core/scraper/db_django.py)
# 說明：以 Django ORM update_or_create 機制實作，防止資料重複寫入，適配多資料庫路由
# ==============================================================================

import logging
from typing import Dict, List
import numpy as np
from stock_db.models import CompanyProfile, CompanyCalendar, CompanyNews, TechnicalAnalysis

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

    def upsert_technical_analysis(self, stock_id: str, df) -> int:
        """寫入技術分析資料，遇到重複主鍵則更新 (使用 Django ORM)"""
        if df is None or df.empty:
            logger.info("No technical analysis data to write.")
            return 0

        # 將 Pandas 的 NaN 轉為 None
        df = df.replace({np.nan: None})

        try:
            stock = CompanyProfile.objects.get(stock_id=stock_id)
        except CompanyProfile.DoesNotExist:
            logger.warning(f"CompanyProfile for {stock_id} does not exist. Cannot write TA.")
            return 0

        # 準備 Bulk Create 資料
        records = []
        for _, row in df.iterrows():
            records.append(TechnicalAnalysis(
                stock=stock,
                trade_date=row['Date'],
                #volume=row.get('Volume'),
                volume=round(row.get('Volume')*0.001),
                #volume=row.get('RegularMarketVolume'),
                open_price=row.get('Open'),
                high_price=row.get('High'),
                low_price=row.get('Low'),
                close_price=row.get('Close'),
                k_value=row.get('K'),
                d_value=row.get('D'),
                j_value=row.get('J'),
                macd=row.get('MACD'),
                macd_signal=row.get('MACD_Signal'),
                bias=row.get('BIAS'),
                williams_r=row.get('Williams_R'),
                bbi=row.get('BBI'),
                cdp=row.get('CDP'),
                ah=row.get('AH'),
                nh=row.get('NH'),
                nl=row.get('NL'),
                al=row.get('AL'),
                pdi=row.get('PDI'),
                mdi=row.get('MDI'),
                adx=row.get('ADX')
            ))

        try:
            # Django 4.1+ 支援 bulk_create update_conflicts
            # 在 MySQL/MariaDB 驅動下，無需且不支援指定 unique_fields 參數
            TechnicalAnalysis.objects.bulk_create(
                records,
                update_conflicts=True,
                update_fields=[
                    'volume', 'open_price', 'high_price', 'low_price', 'close_price',
                    'k_value', 'd_value', 'j_value', 'macd', 'macd_signal', 'bias',
                    'williams_r', 'bbi', 'cdp', 'ah', 'nh', 'nl', 'al', 'pdi', 'mdi', 'adx'
                ]
            )
            return len(records)
        except Exception as e:
            logger.error(f"Failed bulk_create technical analysis for {stock_id}: {e}")
            # Fallback 到 update_or_create 逐筆寫入
            logger.info("Falling back to update_or_create for TA data...")
            written = 0
            for record in records:
                try:
                    TechnicalAnalysis.objects.update_or_create(
                        stock=record.stock,
                        trade_date=record.trade_date,
                        defaults={
                            'volume': record.volume,
                            'open_price': record.open_price,
                            'high_price': record.high_price,
                            'low_price': record.low_price,
                            'close_price': record.close_price,
                            'k_value': record.k_value,
                            'd_value': record.d_value,
                            'j_value': record.j_value,
                            'macd': record.macd,
                            'macd_signal': record.macd_signal,
                            'bias': record.bias,
                            'williams_r': record.williams_r,
                            'bbi': record.bbi,
                            'cdp': record.cdp,
                            'ah': record.ah,
                            'nh': record.nh,
                            'nl': record.nl,
                            'al': record.al,
                            'pdi': record.pdi,
                            'mdi': record.mdi,
                            'adx': record.adx
                        }
                    )
                    written += 1
                except Exception as ex:
                    logger.warning(f"Failed to upsert single TA row: {ex}")
            return written

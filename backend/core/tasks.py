# ==============================================================================
# Celery 任務定義檔 (backend/core/tasks.py)
# 說明：定義單一股票更新任務與定時更新所有排程股票任務
# ==============================================================================

import logging
import time
from celery import shared_task
from stock_db.models import StockScheduleList, CompanyProfile
from core.scraper.fetcher import StockProfileFetcher
from core.scraper.db_django import DjangoDatabaseManager
from stock_db.scraper.ta_analyzer import TAAnalyzer

logger = logging.getLogger(__name__)

@shared_task(name="core.tasks.update_single_stock")
def update_single_stock(stock_id: str) -> str:
    """
    抓取並更新單一股票代碼的公司資料、行事曆與新聞公告
    """
    logger.info(f"開始排程更新股票 {stock_id}...")
    try:
        fetcher = StockProfileFetcher()
        db_manager = DjangoDatabaseManager()

        # 1. 抓取基本資料
        profile = fetcher.fetch_profile(stock_id)
        if not profile:
            logger.warning(f"股票 {stock_id} 未抓取到基本資料，跳過更新。")
            return f"Stock {stock_id} failed: No profile data"

        # 2. 抓取行事曆
        calendar = fetcher.fetch_calendar(stock_id)

        # 3. 抓取新聞與公告
        company_name = profile.get('company_name', stock_id)
        news, announcements = fetcher.fetch_news_and_announcements(stock_id, company_name)

        # 4. 寫入資料庫 (ORM)
        db_manager.upsert_profile(profile)
        db_manager.upsert_calendars(calendar)
        db_manager.upsert_news(news + announcements)

        # 5. 抓取並更新技術分析資料 (依據 StockScheduleList 的 analysis_period 年限)
        schedule_item = StockScheduleList.objects.filter(stock_id=stock_id).first()
        analysis_period = schedule_item.analysis_period if schedule_item else 3
        
        logger.info(f"開始抓取股票 {stock_id} 近 {analysis_period} 年技術分析資料...")
        ta_analyzer = TAAnalyzer()
        ta_df = ta_analyzer.calculate_ta(stock_id, f"{analysis_period}y")
        if ta_df is not None and not ta_df.empty:
            written_ta = db_manager.upsert_technical_analysis(stock_id, ta_df)
            logger.info(f"股票 {stock_id} 技術分析資料成功更新，共 {written_ta} 筆！")
        else:
            logger.warning(f"股票 {stock_id} 未抓取到技術分析資料。")

        logger.info(f"股票 {stock_id} 資訊成功更新！")
        return f"Stock {stock_id} updated successfully"
    except Exception as e:
        logger.error(f"排程更新股票 {stock_id} 失敗: {e}", exc_info=True)
        return f"Stock {stock_id} failed: {e}"


@shared_task(name="core.tasks.update_all_scheduled_stocks")
def update_all_scheduled_stocks() -> str:
    """
    定時任務：定時更新所有在「排程更新清單」中的股票
    """
    logger.info("開始執行所有排程股票的自動更新...")
    scheduled_stocks = StockScheduleList.objects.all()
    if not scheduled_stocks.exists():
        logger.info("排程更新清單中無股票資料，結束任務。")
        return "No stocks scheduled"

    success_count = 0
    fail_count = 0

    for item in scheduled_stocks:
        stock_id = item.stock_id
        logger.info(f"執行更新排程中的股票: {stock_id}")
        
        # 執行更新
        result = update_single_stock(stock_id)
        if "successfully" in result:
            success_count += 1
        else:
            fail_count += 1
        
        # 避免請求過於頻繁
        time.sleep(2)

    msg = f"所有排程股票更新完成。成功: {success_count} 筆, 失敗: {fail_count} 筆"
    logger.info(msg)
    return msg

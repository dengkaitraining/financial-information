# ==============================================================================
# Django 核心與股票資料 API 視圖處理函式 (backend/core/views.py)
# ==============================================================================

import sys
import logging
from django.http import HttpResponse, JsonResponse
from django.db import connection
from django.core.cache import cache
from django.shortcuts import render, get_object_or_404
from django.views.decorators.clickjacking import xframe_options_exempt

from stock_db.models import CompanyProfile, CompanyCalendar, CompanyNews, StockScheduleList

logger = logging.getLogger(__name__)

def home_view(request):
    """
    根目錄 (/) 視圖處理函式
    回傳簡單文字資訊："Django + Vue.js Web 資訊系統開發環境的服務已啟用。"
    """
    return HttpResponse(
        "Django + Vue.js Web 資訊系統開發環境的服務已啟用。",
        content_type="text/plain; charset=utf-8"
    )


def health_check(request):
    """
    健康檢查 API 視圖函式 (/api/status/)
    動態檢測 MariaDB 與 Redis 連線狀態，傳回系統資訊 JSON 格式
    """
    db_status = "unknown"
    db_error = None
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = "error"
        db_error = str(e)

    redis_status = "unknown"
    redis_error = None
    try:
        cache.set("health_check_key", "working", timeout=10)
        val = cache.get("health_check_key")
        if val == "working":
            redis_status = "connected"
        else:
            redis_status = "error"
            redis_error = "Redis 寫入成功但讀取值不一致"
    except Exception as e:
        redis_status = "error"
        redis_error = str(e)

    return JsonResponse({
        "status": "online",
        "django_version": "5.2 LTS",
        "python_version": sys.version,
        "database": {
            "status": db_status,
            "error": db_error,
            "engine": connection.settings_dict.get('ENGINE'),
            "host": connection.settings_dict.get('HOST'),
            "name": connection.settings_dict.get('NAME'),
        },
        "redis": {
            "status": redis_status,
            "error": redis_error,
        }
    })


def stock_fetch_api(request):
    """
    股票基本資料查詢與即時更新 API (/api/stock/fetch/)
    支援：
      GET /api/stock/fetch/?stock_id=2330&update=true  (觸發非同步 Celery 背景任務)
      GET /api/stock/fetch/?stock_id=2330&update=false (查詢本機資料庫)
    """
    stock_id = request.GET.get('stock_id', '').strip()
    update_mode = request.GET.get('update', 'false').lower() == 'true'

    if not stock_id:
        return JsonResponse({"success": False, "error": "請提供股票代碼 (stock_id)"}, status=400)

    if not stock_id.isdigit():
        return JsonResponse({"success": False, "error": "股票代碼必須為數字"}, status=400)

    # 1. 即時更新模式: 發送非同步任務至 Celery
    if update_mode:
        try:
            logger.info(f"觸發 Celery 背景更新股票資料: {stock_id}")
            from .tasks import update_single_stock
            
            # 使用 delay 非同步發送任務，避免 HTTP 阻塞
            update_single_stock.delay(stock_id)

            # 自動將該股票代碼加入「排程更新清單」
            StockScheduleList.objects.get_or_create(stock_id=stock_id)

            return JsonResponse({
                "success": True,
                "task_started": True,
                "msg": f"已啟動股票 {stock_id} 背景即時抓取更新，請稍候..."
            })
        except Exception as e:
            logger.error(f"觸發背景更新股票 {stock_id} 失敗: {e}", exc_info=True)
            return JsonResponse({"success": False, "error": f"更新失敗: {str(e)}"}, status=500)

    # 2. 本地查詢模式
    try:
        profile = CompanyProfile.objects.filter(stock_id=stock_id).first()
        if not profile:
            return JsonResponse({
                "success": True,
                "has_data": False,
                "msg": "本機資料庫無此股票資料，請點擊「即時更新並儲存」"
            })

        # 序列化 Profile 25 欄位
        profile_dict = {
            "stock_id": profile.stock_id,
            "tax_id": profile.tax_id,
            "company_name": profile.company_name,
            "spokesperson": profile.spokesperson,
            "eng_short_name": profile.eng_short_name,
            "deputy_spokesperson": profile.deputy_spokesperson,
            "establishment_date": profile.establishment_date.strftime('%Y-%m-%d') if profile.establishment_date else None,
            "phone": profile.phone,
            "listing_date": profile.listing_date.strftime('%Y-%m-%d') if profile.listing_date else None,
            "fax": profile.fax,
            "industry_category": profile.industry_category,
            "website": profile.website,
            "chairman": profile.chairman,
            "email": profile.email,
            "general_manager": profile.general_manager,
            "stock_transfer_agent": profile.stock_transfer_agent,
            "capital": float(profile.capital) if profile.capital else None,
            "auditor": profile.auditor,
            "issued_shares": profile.issued_shares,
            "address": profile.address,
            "market_cap_millions": float(profile.market_cap_millions) if profile.market_cap_millions else None,
            "market_type": profile.market_type,
            "insider_holding_ratio": float(profile.insider_holding_ratio) if profile.insider_holding_ratio else None,
            "group_name": profile.group_name,
            "main_business": profile.main_business,
            "created_at": profile.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": profile.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        }

        # 擷取近 10 筆行事曆
        calendars = list(CompanyCalendar.objects.filter(stock=profile).order_by('event_date')[:10].values(
            'event_type', 'event_date', 'description'
        ))
        for cal in calendars:
            cal['event_date'] = cal['event_date'].strftime('%Y-%m-%d')

        # 擷取近 10 筆新聞/公告 (依發布日期降序)
        news_items = list(CompanyNews.objects.filter(stock=profile).order_by('-published_date')[:10].values(
            'news_type', 'title', 'url', 'publisher', 'published_date', 'summary'
        ))
        from django.utils import timezone
        for n in news_items:
            if n['published_date']:
                local_dt = timezone.localtime(n['published_date'])
                n['published_date'] = local_dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                n['published_date'] = None

        # 擷取歷史技術分析資料 (依交易日期升序)
        from stock_db.models import TechnicalAnalysis
        ta_list = list(TechnicalAnalysis.objects.filter(stock=profile).order_by('trade_date').values(
            'trade_date', 'volume', 'open_price', 'high_price', 'low_price', 'close_price',
            'k_value', 'd_value', 'j_value', 'macd', 'macd_signal', 'bias', 'williams_r', 'bbi',
            'cdp', 'ah', 'nh', 'nl', 'al', 'pdi', 'mdi', 'adx'
        ))
        for ta in ta_list:
            ta['trade_date'] = ta['trade_date'].strftime('%Y-%m-%d')
            # 轉換 Decimal 欄位為 float
            for key in ['open_price', 'high_price', 'low_price', 'close_price', 'k_value', 'd_value', 'j_value',
                        'macd', 'macd_signal', 'bias', 'williams_r', 'bbi', 'cdp', 'ah', 'nh', 'nl', 'al',
                        'pdi', 'mdi', 'adx']:
                if ta[key] is not None:
                    ta[key] = float(ta[key])

        # 檢查是否已在排程中
        in_schedule = StockScheduleList.objects.filter(stock_id=stock_id).exists()

        return JsonResponse({
            "success": True,
            "has_data": True,
            "in_schedule": in_schedule,
            "profile": profile_dict,
            "calendar": calendars,
            "news": news_items,
            "technical_analysis": ta_list
        })
    except Exception as e:
        logger.error(f"查詢股票 {stock_id} 失敗: {e}", exc_info=True)
        return JsonResponse({"success": False, "error": f"查詢失敗: {str(e)}"}, status=500)


@xframe_options_exempt
def stock_calendar_view(request, stock_id):
    """
    更多行事曆頁面 (/stock/calendar/<stock_id>/)
    """
    profile = get_object_or_404(CompanyProfile, stock_id=stock_id)
    calendars = CompanyCalendar.objects.filter(stock=profile).order_by('event_date')
    return render(request, 'stock_calendar.html', {
        'profile': profile,
        'calendars': calendars
    })


@xframe_options_exempt
def stock_news_view(request, stock_id):
    """
    更多新聞與公告頁面 (/stock/news/<stock_id>/)
    """
    profile = get_object_or_404(CompanyProfile, stock_id=stock_id)
    news_list = CompanyNews.objects.filter(stock=profile).order_by('-published_date')
    return render(request, 'stock_news.html', {
        'profile': profile,
        'news_list': news_list
    })

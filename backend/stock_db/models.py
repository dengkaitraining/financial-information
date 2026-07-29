# ==============================================================================
# 股票資料庫模型定義 (backend/stock_db/models.py)
# 說明：定義台股公司基本資料、行事曆、新聞公告、技術分析及排程更新清單 Models
# ==============================================================================

from django.db import models

class CompanyProfile(models.Model):
    """
    1. 公司基本資料表
    """
    stock_id = models.CharField(max_length=20, primary_key=True, verbose_name="股票代碼")
    tax_id = models.CharField(max_length=20, null=True, blank=True, verbose_name="統一編號")
    company_name = models.CharField(max_length=100, verbose_name="公司名稱")
    spokesperson = models.CharField(max_length=50, null=True, blank=True, verbose_name="發言人")
    eng_short_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="英文簡稱")
    deputy_spokesperson = models.CharField(max_length=50, null=True, blank=True, verbose_name="代理發言人")
    establishment_date = models.DateField(null=True, blank=True, verbose_name="成立時間")
    phone = models.CharField(max_length=30, null=True, blank=True, verbose_name="總機電話")
    listing_date = models.DateField(null=True, blank=True, verbose_name="掛牌日期")
    fax = models.CharField(max_length=30, null=True, blank=True, verbose_name="傳真號碼")
    industry_category = models.CharField(max_length=50, null=True, blank=True, verbose_name="產業類別")
    website = models.CharField(max_length=255, null=True, blank=True, verbose_name="公司網站")
    chairman = models.CharField(max_length=50, null=True, blank=True, verbose_name="董事長")
    email = models.CharField(max_length=100, null=True, blank=True, verbose_name="電子郵件")
    general_manager = models.CharField(max_length=50, null=True, blank=True, verbose_name="總經理")
    stock_transfer_agent = models.CharField(max_length=100, null=True, blank=True, verbose_name="股務代理")
    capital = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="股本(元)")
    auditor = models.CharField(max_length=100, null=True, blank=True, verbose_name="簽證會計師")
    issued_shares = models.BigIntegerField(null=True, blank=True, verbose_name="已發行普通股數")
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name="公司地址")
    market_cap_millions = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="市值(百萬)")
    market_type = models.CharField(max_length=20, null=True, blank=True, verbose_name="市場別")
    insider_holding_ratio = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="董監持股比例(%)")
    group_name = models.CharField(max_length=100, null=True, blank=True, verbose_name="所屬集團")
    main_business = models.TextField(null=True, blank=True, verbose_name="主要經營業務")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        db_table = 'company_profile'
        verbose_name = "公司基本資料"
        verbose_name_plural = "公司基本資料"

    def __str__(self):
        return f"{self.stock_id} {self.company_name}"


class CompanyCalendar(models.Model):
    """
    2. 公司行事曆資料表
    """
    id = models.BigAutoField(primary_key=True)
    stock = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, db_column='stock_id', related_name='calendars', verbose_name="公司")
    event_type = models.CharField(max_length=50, verbose_name="事件類型")  # 股東常會/配股發放日/現金股利發放日
    event_date = models.DateField(verbose_name="事件日期")
    description = models.TextField(null=True, blank=True, verbose_name="補充說明")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        db_table = 'company_calendar'
        unique_together = ('stock', 'event_type', 'event_date')
        verbose_name = "公司行事曆"
        verbose_name_plural = "公司行事曆"

    def __str__(self):
        return f"{self.stock.stock_id} - {self.event_type} ({self.event_date})"


class CompanyNews(models.Model):
    """
    3. 公司新聞與個股公告表
    """
    id = models.BigAutoField(primary_key=True)
    stock = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, db_column='stock_id', related_name='news', verbose_name="公司")
    news_type = models.CharField(max_length=100, verbose_name="類型")  # NEWS / ANNOUNCEMENT
    title = models.TextField(verbose_name="標題")
    url = models.TextField(verbose_name="新聞連結 URL")
    publisher = models.CharField(max_length=500, null=True, blank=True, verbose_name="發布來源")
    published_date = models.DateTimeField(null=True, blank=True, verbose_name="發布時間")
    summary = models.TextField(null=True, blank=True, verbose_name="內文摘要")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        db_table = 'company_news'
        verbose_name = "公司新聞與個股公告"
        verbose_name_plural = "公司新聞與個股公告"

    def __str__(self):
        return f"{self.stock.stock_id} - {self.title[:30]}"


class StockScheduleList(models.Model):
    """
    4. 排程更新的股票清單 (新增 analysis_period 欄位，預設為 3)
    """
    stock_id = models.CharField(max_length=20, primary_key=True, verbose_name="股票代碼")
    analysis_period = models.IntegerField(default=3, verbose_name="技術分析抓取區間(年)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        db_table = 'stock_schedule_list'
        verbose_name = "排程更新清單"
        verbose_name_plural = "排程更新清單"

    def __str__(self):
        return self.stock_id


class TechnicalAnalysis(models.Model):
    """
    5. 個股技術分析資料表 (對應 schema.sql 欄位)
    """
    id = models.BigAutoField(primary_key=True)
    stock = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, db_column='stock_id', related_name='technical_analyses', verbose_name="公司")
    trade_date = models.DateField(verbose_name="交易日期")
    
    # 基本價量
    volume = models.BigIntegerField(null=True, blank=True, verbose_name="成交量")
    open_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="開盤價")
    high_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="最高價")
    low_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="最低價")
    close_price = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="收盤價")
    
    # KD, J
    k_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="K值")
    d_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="D值")
    j_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="J值")
    
    # MACD
    macd = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="MACD")
    macd_signal = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="MACD Signal")
    
    # BIAS, Williams, BBI
    bias = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="乖離率(6日)")
    williams_r = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="威廉指標(14日)")
    bbi = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="多空指標(BBI)")
    
    # CDP
    cdp = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="CDP")
    ah = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="最高值(AH)")
    nh = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="近高值(NH)")
    nl = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="近低值(NL)")
    al = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, verbose_name="最低值(AL)")
    
    # DMI
    pdi = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="+DI")
    mdi = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="-DI")
    adx = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True, verbose_name="ADX")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        db_table = 'technical_analysis'
        unique_together = ('stock', 'trade_date')
        verbose_name = "個股技術分析"
        verbose_name_plural = "個股技術分析"
        ordering = ['-trade_date']

    def __str__(self):
        return f"{self.stock.stock_id} - {self.trade_date}"

# ==============================================================================
# 核心模組 Django Model與權限宣告 (backend/core/models.py)
# 說明：定義『資料庫與表單管理』進階群組權限與台股公司基本資料相關資料表
# ==============================================================================

from django.db import models

class DatabaseManagerPermission(models.Model):
    """
    虛擬 Model: 用於宣告資料庫與表單管理功能之群組權限
    """
    class Meta:
        managed = False
        default_permissions = ()
        permissions = [
            ("can_manage_db_tables", "可以管理資料庫與表單資料 (DataTables & 帳號切換)"),
        ]


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
        return f"{self.stock_id} - {self.event_type} ({self.event_date})"


class CompanyNews(models.Model):
    """
    3. 公司新聞與個股公告表
    """
    id = models.BigAutoField(primary_key=True)
    stock = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, db_column='stock_id', related_name='news', verbose_name="公司")
    news_type = models.CharField(max_length=100, verbose_name="類型")  # NEWS / ANNOUNCEMENT
    title = models.TextField(verbose_name="標題")
    url = models.CharField(max_length=500, verbose_name="新聞連結 URL")
    publisher = models.CharField(max_length=500, null=True, blank=True, verbose_name="發布來源")
    published_date = models.DateTimeField(null=True, blank=True, verbose_name="發布時間")
    summary = models.TextField(null=True, blank=True, verbose_name="內文摘要")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        db_table = 'company_news'
        unique_together = ('stock', 'url')
        verbose_name = "公司新聞與個股公告"
        verbose_name_plural = "公司新聞與個股公告"

    def __str__(self):
        return f"{self.stock_id} - {self.title[:30]}"


class StockScheduleList(models.Model):
    """
    4. 排程更新的股票清單
    """
    stock_id = models.CharField(max_length=20, primary_key=True, verbose_name="股票代碼")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    class Meta:
        db_table = 'stock_schedule_list'
        verbose_name = "排程更新清單"
        verbose_name_plural = "排程更新清單"

    def __str__(self):
        return self.stock_id

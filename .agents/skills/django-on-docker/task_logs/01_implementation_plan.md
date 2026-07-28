# 台股個股技術分析 (Technical Analysis) 搜尋、儲存、排程與 ECharts 戰情室系統實作計畫 (01_implementation_plan.md)

本計畫旨在依據 `<spec>` 需求，在既有環境下擴充「個股技術分析 (Technical Analysis)」單元。我們將新建一個獨立的 Django App `stock_db`，將所有與股票資料相關的模型（包括原本 core 裡的 profile 模型以及新建立的技術分析模型）移入該 App 中進行統一 migration 管理；在後端整合非同步/定期排程爬取與格式清洗落庫；並在前台使用 Apache ECharts 繪製包含 K線、CDP、BBI、成交量、KD、MACD、BIAS、威廉與 DMI 指標的綜合技術分析圖表。

---

## 📌 系統架構設計

### 1. 新建 `stock_db` App 與 Models 搬遷重構 (符合需求 8)
我們將建立一個獨立的 Django App `stock_db`，以擁有專屬 of `stock_db/migrations/` 資料夾。我們將把有關台股的所有模型移入並重新整理：
* **`CompanyProfile`**、**`CompanyCalendar`**、**`CompanyNews`**：從 `core/models.py` 移入 `stock_db/models.py`。
* **`StockScheduleList`**：移入 `stock_db/models.py`，並新增 `analysis_period = models.IntegerField(default=3)` 欄位，代表抓取技術分析之歷史年限。
* **`TechnicalAnalysis`**：定義個股技術分析模型，欄位對應 `schema.sql` 結構。
* **Scraper 移入獨立 App**：為了架構的高可維護性，原 core app 下的 `fetcher.py` 與 `translator.py` 移動至 `stock_db/scraper/`。

### 2. 時區與時間對齊 台灣時間 (UTC+8)
* 為 Python/Celery 容器加載 `TZ=Asia/Taipei` 系統時區，將 Django settings 中 Celery 設定為 `CELERY_ENABLE_UTC = False`，確保定時任務排程在台灣本地時間運作。
* 新聞與公告發布日期 `published_date` 在 `fetcher.py` 寫入時及 views.py 序列化回傳時，全面透過時區工具轉換為台北時間。

### 3. DataTables 分頁與 12pt 最小字體強制限制
* 「重大行事曆」與「新聞公告」更多新分頁中使用 DataTables 提供每頁項數控制與快速搜尋，並客製化為深色霓虹樣式。
* 所有前台小字體類別（如 `.text-xs`, `.text-sm`）統一覆寫強制最小為 `12pt !important` (16px)。

### 4. 爬蟲延遲與 Race Condition 輪詢修復
* 在 Scraper 各函式中加上 `time.sleep(5)`，排程更新時個股之間加上 `time.sleep(10)`，排程週期設定為每 4 小時一次。
* 解決 Race Condition：後端 views.py 在輪詢時要求 `profile` 和 `has_ta` 共同為 True 才判定 `has_data: true`；前端輪詢成功後自動發起一輪純查詢（再次抓取）以解決圖表因落庫差無法顯示的痛點。

---

## 📂 Proposed Changes

### 🔧 基礎環境與 App 建立

#### [MODIFY] [settings.py](file:///home/dengkai/projects/financial-information/backend/core/settings.py)
* 註冊 `stock_db` 並配置 `CELERY_ENABLE_UTC = False`。

#### [NEW] [models.py](file:///home/dengkai/projects/financial-information/backend/stock_db/models.py)
* 定義重構搬遷的所有股票與技術分析模型。

#### [NEW] [fetcher.py](file:///home/dengkai/projects/financial-information/backend/stock_db/scraper/fetcher.py)
* 從 core 搬移至此，支援 5 秒防封鎖延遲與台北時區時間轉化。

#### [NEW] [translator.py](file:///home/dengkai/projects/financial-information/backend/stock_db/scraper/translator.py)
* 移動至 stock_db scraper 目錄。

---

### 🌐 路由、API 與前端

#### [MODIFY] [views.py](file:///home/dengkai/projects/financial-information/backend/core/views.py)
* 改進 `/api/stock/fetch/` 雙重 is_ta 檢測以防輪詢 Race Condition，並格式化新聞時間為台北時間。

#### [MODIFY] [App.vue](file:///home/dengkai/projects/financial-information/frontend/src/App.vue)
* 實施 12pt 最小字體強制，並在輪詢結束後調用 `await handleStockSearch(false)` 再次抓取資料。
* 名稱旁顯示最新收盤價與漲跌幅看板。

#### [MODIFY] [stock_calendar.html](file:///home/dengkai/projects/financial-information/backend/templates/stock_calendar.html) 與 [stock_news.html](file:///home/dengkai/projects/financial-information/backend/templates/stock_news.html)
* 導入 DataTables 深色自適應分頁，限制最小字體 12pt。

---

## 🧪 Verification Plan

### Automated Tests
* 執行單元測試命令：
  ```bash
  docker compose exec fin-backend python manage.py test stock_db
  ```

### Manual Verification
1. 進入 Unfold 後台驗證定期任務（Periodic tasks）已自動初始化為每 4 小時一次。
2. 造訪戰情室即時更新股票代碼，確認輪詢順暢，圖表與股價看板在更新完畢時一次性完整顯示。

# 台股公司基本資料 profile 搜尋、儲存、排程與戰情室系統實作計畫

本計畫旨在依據 `<spec>` 需求，在既有的 Docker Compose 容器化 Django + Vue.js 開發環境中，建立搜尋、儲存、排程「公司基本資料 profile 資料」的模組。本實作將使用 Django 5.2 LTS, Django Unfold 後台, Celery, Django Celery Beat 與 Vue 3.5。

---

## 系統架構設計

我們將採用 Django ORM 來管理「公司基本資料」、「公司行事曆」、「公司新聞與個股公告」以及「排程更新清單」等表單。此舉將完全相容於 Django Unfold 的後台管理介面，並能夠透過 `django-celery-beat` 元件在後台以圖形化介面配置 Crontab 排程任務。

### 1. 資料庫模型與 Migration 機制
所有資料表預設建立於 `default` 資料庫中（即 `user_stock_db`，由 `PrimaryEmployeeRouter` 自動路由）。
我們將**完全使用 Django Models** 定義這四個資料表。如此一來，即可透過 Django 內建的 `python manage.py makemigrations` 與 `python manage.py migrate` 機制管理表單的建立與版控，完美整合 Django migration 機制：
* **`CompanyProfile`** (公司基本資料表):
  * `stock_id` (股票代碼, 主鍵)
  * `company_name` (公司名稱)、`tax_id` (統一編號)、`spokesperson` (發言人)、`eng_short_name` (英文簡稱)、`deputy_spokesperson` (代理發言人)、`establishment_date` (成立時間)、`phone` (總機電話)、`listing_date` (掛牌日期)、`fax` (傳真號碼)、`industry_category` (產業類別)、`website` (公司網站)、`chairman` (董事長)、`email` (電子郵件)、`general_manager` (總經理)、`stock_transfer_agent` (股務代理)、`capital` (股本)、`auditor` (簽證會計師)、`issued_shares` (已發行普通股數)、`address` (地址)、`market_cap_millions` (市值百萬)、`market_type` (市場別)、`insider_holding_ratio` (董監持股比例)、`group_name` (所屬集團)、`main_business` (主要經營業務)
* **`CompanyCalendar`** (公司行事曆資料表):
  * 外鍵關聯至 `CompanyProfile` (`stock_id`)
  * `event_type` (事件類型: 股東常會 / 配股發放日 / 現金股利發放日)
  * `event_date` (事件日期)
  * `description` (補充說明)
  * 聯合唯一約束：`(stock_id, event_type, event_date)`
* **`CompanyNews`** (公司新聞與個股公告資料表):
  * 外鍵關聯至 `CompanyProfile` (`stock_id`)
  * `news_type` (類型: NEWS / ANNOUNCEMENT)
  * `title` (標題)
  * `url` (連結 URL, CharField 限制 max_length=500，防範 TEXT 在 Unique 索引中報錯)
  * `publisher` (來源)、`published_date` (發布時間)、`summary` (摘要)
  * 聯合唯一約束：`(stock_id, url)`
* **`StockScheduleList`** (排程更新清單):
  * `stock_id` (股票代碼, 主鍵)

### 2. 定時排程機制 (Celery + Celery Beat)
* 在 `docker-compose.yaml` 中新增 `fin-celery-worker` 與 `fin-celery-beat` 服務，共享 `fin-backend` 容器的環境與代碼。
* 在 `core/tasks.py` 建立：
  * `core.tasks.update_single_stock(stock_id)`: 負責執行指定股票代碼的爬蟲抓取、英翻中及資料庫 upsert (ORM)。
  * `core.tasks.update_all_scheduled_stocks()`: 遍歷 `StockScheduleList` 中的股票，呼叫並更新各檔股票。
* 在 Django Unfold 中重新註冊 `django-celery-beat` 的管理介面，讓管理員可以直接設定 Crontab 定時任務。

### 3. 前端戰情室 Dashboard (Vue 3.5)
* 於 `frontend/src/App.vue` 中整合「公司基本資料戰情室」介面，採用 **極致深色科技感 (Glassmorphism & Neon Glow)** 的現代 UI。
* 包含股票搜尋輸入框，支援：
  * **「搜尋」按鈕**：自 Django API 讀取本機資料。
  * **「即時更新並儲存」按鈕**：發送請求至後端觸發即時爬蟲與資料落庫，並將該股票自動加入排程清單。
* 顯示公司基本資料 (以精緻的 Grid 呈現 25 項欄位)、行事曆 (近10筆) 與新聞公告 (近10筆)。
* 行事曆與新聞各自附帶 **"More"** 按鈕，點擊後會透過 `window.open` 開啟後端渲染的新分頁，列出全部資訊。

### 4. 後端 More 資訊頁面 (Django Template + Tailwind)
* 新增 `/stock/calendar/<stock_id>/` 與 `/stock/news/<stock_id>/` 路由與 View，回傳精美渲染的 Full List 頁面，搭配 Tailwind CSS 與現代深色戰情室風格，與前台完美呼應。

---

## Proposed Changes

### 🔧 基礎相依性與環境配置

#### [MODIFY] [requirements.txt](file:///home/dengkai/projects/financial-information/backend/requirements.txt)
* 新增 `celery` 與 `django-celery-beat` 函式庫。

#### [MODIFY] [docker-compose.yaml](file:///home/dengkai/projects/financial-information/docker-compose.yaml)
* 於 `services` 中新增 `fin-celery-worker` 與 `fin-celery-beat` 容器。

#### [MODIFY] [settings.py](file:///home/dengkai/projects/financial-information/backend/core/settings.py)
* `INSTALLED_APPS` 內註冊 `django_celery_beat`。
* 配置 `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`, `CELERY_BEAT_SCHEDULER` 參數。

#### [NEW] [celery.py](file:///home/dengkai/projects/financial-information/backend/core/celery.py)
* 初始化 Celery 應用，載入 Django 設定，並開啟自動探測。

#### [MODIFY] [__init__.py](file:///home/dengkai/projects/financial-information/backend/core/__init__.py)
* 於套件初始化時載入 `celery_app`，使其隨 Django 啟動。

---

### 📦 資料庫與爬蟲整合

#### [MODIFY] [models.py](file:///home/dengkai/projects/financial-information/backend/core/models.py)
* 定義 `CompanyProfile`, `CompanyCalendar`, `CompanyNews`, `StockScheduleList`。

#### [NEW] [db_django.py](file:///home/dengkai/projects/financial-information/backend/core/scraper/db_django.py)
* 實作使用 Django ORM (update_or_create) 的 upsert 機制，取代 `MySQLdb` 寫入。

#### [NEW] [fetcher.py](file:///home/dengkai/projects/financial-information/backend/core/scraper/fetcher.py)
* 移植原 `.backend_ver/corp_scraper/v2/items/1-profile/fetcher.py` 內容。

#### [NEW] [translator.py](file:///home/dengkai/projects/financial-information/backend/core/scraper/translator.py)
* 移植原 `.backend_ver/corp_scraper/v2/items/1-profile/translator.py` 內容。

#### [NEW] [tasks.py](file:///home/dengkai/projects/financial-information/backend/core/tasks.py)
* 建立 Celery 任務 `update_single_stock` 與 `update_all_scheduled_stocks`。

#### [NEW] [admin.py](file:///home/dengkai/projects/financial-information/backend/core/admin.py)
* 註冊自定義 Models 到 Unfold Admin；並用 Unfold 樣式重新接管 `PeriodicTask` 與 `CrontabSchedule`。

---

### 🌐 路由、API 與前端展示

#### [MODIFY] [views.py](file:///home/dengkai/projects/financial-information/backend/core/views.py)
* 實作 `/api/stock/fetch/` JSON API，處理搜尋與即時更新邏輯。
* 實作 `/stock/calendar/<stock_id>/` 與 `/stock/news/<stock_id>/` 視圖，查詢並渲染所有行事曆與新聞。

#### [MODIFY] [urls.py](file:///home/dengkai/projects/financial-information/backend/core/urls.py)
* 註冊 API 路由與 HTML 詳情分頁路由。

#### [NEW] [stock_calendar.html](file:///home/dengkai/projects/financial-information/backend/templates/stock_calendar.html)
* 渲染該股票全部行事曆的精美 HTML 範本。

#### [NEW] [stock_news.html](file:///home/dengkai/projects/financial-information/backend/templates/stock_news.html)
* 渲染該股票全部新聞公告的精美 HTML 範本。

#### [MODIFY] [App.vue](file:///home/dengkai/projects/financial-information/frontend/src/App.vue)
* 整合「公司基本資料戰情室」UI。
* 串接後端 API，支援股票搜尋、即時更新。
* 實作 "More" 按鈕跳轉至對應詳細頁面。

---

## Verification Plan

### Automated Tests
* 在 `backend/core/tests.py` 新增單元測試：
  * 測試 `CompanyProfile`, `CompanyCalendar`, `CompanyNews`, `StockScheduleList` 的 ORM 功能與欄位約束。
  * 測試 `/api/stock/fetch/` 的正常查詢與即時更新 API。
  * 測試行事曆與新聞詳情頁面渲染。
* 執行測試指令：
  ```bash
  docker compose exec fin-backend python manage.py test core
  ```

### Manual Verification
1. 建立 Migrations 並執行遷移：
   ```bash
   docker compose exec fin-backend python manage.py makemigrations core
   docker compose exec fin-backend python manage.py migrate
   ```
2. 重建並啟動容器：
   ```bash
   docker compose down
   docker compose up -d --build
   ```
3. 進入 Django Unfold 後台 (`http://localhost/admin/`)：
   - 驗證「公司基本資料」、「公司行事曆」、「公司新聞」、「排程更新清單」等表單的管理功能（新增、修改、刪除）。
   - 驗證 `Periodic tasks` 和 `Crontabs` 可以圖形化操作，新增定時任務。
4. 前台網頁測試 (`http://localhost/tech-stack/`)：
   - 進行股票代碼搜尋（如輸入 `2330` 並搜尋）。
   - 點擊「即時更新並儲存」：驗證資料成功透過 yfinance & GNews 抓取、自動英翻中、儲存至 MariaDB，並順利在戰情室 Dashboard 顯示。
   - 驗證搜尋過的代碼已被寫入「排程更新清單」表中。
   - 點擊「行事曆」和「新聞」區的 `More` 按鈕，驗證會成功開啟新分頁，展示該股票的所有行事曆/新聞公告資料，且頁面風格美觀。

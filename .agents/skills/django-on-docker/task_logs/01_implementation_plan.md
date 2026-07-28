# 台股個股技術分析 (Technical Analysis) 搜尋、儲存、排程與 ECharts 戰情室系統實作計畫 (01_implementation_plan.md)

本計畫旨在依據 `<spec>` 需求，在既有環境下擴充「個股技術分析 (Technical Analysis)」單元。我們將新建一個獨立的 Django App `stock_db`，將所有與股票資料相關的模型（包括原本 core 裡的 profile 模型以及新建立的技術分析模型）移入該 App 中進行統一 migration 管理；在後端整合非同步/定期排程爬取與格式清洗落庫；並在前台使用 Apache ECharts 繪製包含 K線、CDP、BBI、成交量、KD、MACD、BIAS、威廉與 DMI 指標的綜合技術分析圖表。

---

## 📌 系統架構設計

### 1. 新建 `stock_db` App 與 Models 搬遷重構 (符合需求 8)
我們將建立一個獨立的 Django App `stock_db`，以擁有專屬 of `stock_db/migrations/` 資料夾。我們將把有關台股的所有模型移入並重新整理：
* **`CompanyProfile`**、**`CompanyCalendar`**、**`CompanyNews`**：從 `core/models.py` 移入 `stock_db/models.py`。
* **`StockScheduleList`**：移入 `stock_db/models.py`，並新增 `analysis_period = models.IntegerField(default=3)` 欄位，代表抓取技術分析之歷史年限。
* **`TechnicalAnalysis` [NEW]**：定義個股技術分析模型，欄位對應 `schema.sql`：
  * `stock` (外鍵關聯至 `CompanyProfile.stock_id`, `db_column='stock_id'`)
  * `trade_date` (交易日期, DateField)
  * 聯合唯一約束：`unique_together = (('stock', 'trade_date'),)`
  * 價量：`volume`, `open_price`, `high_price`, `low_price`, `close_price`
  * 指標：`k_value`, `d_value`, `j_value`, `macd`, `macd_signal`, `bias`, `williams_r`, `bbi`
  * CDP：`cdp`, `ah`, `nh`, `nl`, `al`
  * DMI：`pdi`, `mdi`, `adx`
* **資料庫路由**：`PrimaryEmployeeRouter` 依然保留，`stock_db` 模型將被自動路由至主要資料庫 `default` (即 `user_stock_db`)，與原本行為完全一致。

### 2. 技術分析 Scraper 移植與異步落庫 (符合需求 3 & 4)
* 建立 `stock_db/scraper/ta_analyzer.py`，移植並微調 yfinance 技術分析指標運算邏輯。
* 當更新股票（即時更新或定時排程）時，將原有的 `update_single_stock` 任務改為：
  1. 擷取並更新 `CompanyProfile`、`CompanyCalendar`、`CompanyNews` 並落庫（維持原邏輯）。
  2. 獲取 `StockScheduleList` 中的 `analysis_period`（例如 3 年）。
  3. 調用 `TAAnalyzer().calculate_ta(stock_id, f"{analysis_period}y")` 擷取前 3 年數據並計算所有技術指標。
  4. 進行數據清洗（如 NaN 轉 None，斜線日期格式清洗為 `YYYY-MM-DD`）。
  5. 使用 Django ORM `bulk_create(..., update_conflicts=True)` 語句一次性高效地 upsert 寫入 `technical_analysis` 表中，保證資料不重複。

### 3. Django Unfold 後台管理 (符合需求 5)
* 於 `stock_db/admin.py` 中註冊這 5 個 Models，使管理員可對技術分析數據與排程進行資料新增、修改與刪除。
* 保留並優化 Unfold 接管的 Celery Beat 圖形化 Crontab 管理界面。

### 4. 前端 Apache ECharts 戰情室分頁 (符合需求 6)
* 於前端容器中安裝 `echarts` 套件，並寫入 `package.json`。
* 於 `/api/stock/fetch/` JSON API 的回傳數據中，額外序列化並包含 `technical_analysis` 的完整歷史數據。
* 修改 `App.vue`：
  * 在戰情室面板中，加入 `📋 基本資料與新聞` 與 `📈 技術分析圖表` 兩個子分頁。
  * 點選 `技術分析圖表` 時，動態初始化一個精美的 **Apache ECharts** 圖表：
    * 採用多個 Grid 垂直佈局，共享 X 軸（交易日期），並加載 `DataZoom` 滑動與縮放控制器。
    * **主圖 (Candlestick + Lines)**：繪製 K 線圖，並重疊繪製 CDP 參考指標（AH / NH / NL / AL）與多空指標（BBI 線）。
    * **子圖 1 (Bar)**：成交量 (Volume) 柱狀圖。
    * **子圖 2 (Line)**：KD, J 線圖 (K / D / J 三條折線)。
    * **子圖 3 (Bar/Line)**：MACD 指標圖（DIF/DEA/MACD柱狀）。
    * **子圖 4 (Line)**：DMI / 乖離率 (BIAS) / 威廉指標 (Williams_R)。

---

## 📂 Proposed Changes

### 🔧 基礎環境與 App 建立

#### [MODIFY] [settings.py](file:///home/dengkai/projects/financial-information/backend/core/settings.py)
* 在 `INSTALLED_APPS` 註冊新建立 the `stock_db` App。

#### [NEW] [apps.py](file:///home/dengkai/projects/financial-information/backend/stock_db/apps.py)
* 建立 `stock_db` 應用設定檔。

#### [NEW] [models.py](file:///home/dengkai/projects/financial-information/backend/stock_db/models.py)
* 定義重構搬遷的 `CompanyProfile`, `CompanyCalendar`, `CompanyNews`, `StockScheduleList`。
* 定義新模型 `TechnicalAnalysis`。

#### [DELETE] [models.py](file:///home/dengkai/projects/financial-information/backend/core/models.py)
* 刪除 `core` app 下的多餘模型，防止 migrations 衝突。

---

### 📦 資料庫遷移、爬蟲與任務

#### [NEW] [migrations/0001_initial.py](file:///home/dengkai/projects/financial-information/backend/stock_db/migrations/0001_initial.py)
* 重新產生 `stock_db` 的初始建表遷移檔案，管理所有股票模型。

#### [NEW] [ta_analyzer.py](file:///home/dengkai/projects/financial-information/backend/stock_db/scraper/ta_analyzer.py)
* 實作技術指標計算、yfinance 擷取封裝。

#### [MODIFY] [db_django.py](file:///home/dengkai/projects/financial-information/backend/core/scraper/db_django.py)
* 移入 `stock_db` 或在此實作 `TechnicalAnalysis` 的 bulk_create/upsert 機制。

#### [MODIFY] [tasks.py](file:///home/dengkai/projects/financial-information/backend/core/tasks.py)
* 更新 `update_single_stock` 任務，在更新 profile 時一併擷取 3 年歷史技術分析指標並落庫。

#### [NEW] [admin.py](file:///home/dengkai/projects/financial-information/backend/stock_db/admin.py)
* 註冊新 models 至 Unfold 後台，提供完整的資料 CRUD 操作界面。

#### [DELETE] [admin.py](file:///home/dengkai/projects/financial-information/backend/core/admin.py)
* 清理 `core` app 下的模型註冊。

---

### 🌐 路由、API 與前端

#### [MODIFY] [views.py](file:///home/dengkai/projects/financial-information/backend/core/views.py)
* 修改 `/api/stock/fetch/`，自 `TechnicalAnalysis` 撈取歷史指標數據並併入 JSON 回傳。

#### [MODIFY] [package.json](file:///home/dengkai/projects/financial-information/frontend/package.json)
* 在 `dependencies` 新增 `"echarts": "^5.5.1"`。

#### [MODIFY] [App.vue](file:///home/dengkai/projects/financial-information/frontend/src/App.vue)
* 整合 ECharts 技術分析圖表分頁。
* 實現多指標 K 線、成交量、KD、MACD、BIAS 等共享 X 軸縮放圖表。

---

## 🧪 Verification Plan

### Automated Tests
* 於 `backend/stock_db/tests.py` 撰寫並擴充單元測試：
  * 測試 `TechnicalAnalysis` ORM 的寫入、外鍵關聯與聯合唯一約束。
  * 測試 `TAAnalyzer` 運算與 `StockScheduleList.analysis_period` 串接之 Mock 爬蟲 API。
* 執行單元測試命令：
  ```bash
  docker compose exec fin-backend python manage.py test stock_db
  ```

### Manual Verification
1. 刪除原有 core 遷移快取以防止多 app 重複建表，並執行 `makemigrations` 與 `migrate`：
   ```bash
   docker compose exec fin-backend python manage.py makemigrations stock_db
   docker compose exec fin-backend python manage.py migrate
   ```
2. 安裝 frontend 容器依賴：
   ```bash
   docker compose exec fin-frontend npm install
   ```
3. 重啟服務容器以啟用最新配置。
4. 進入後台驗證 `technical_analysis` 資料表管理功能，並在圖形化界面嘗試指派 Crontab 任務。
5. 前往 `http://localhost/profile/`，搜尋並即時更新 `2330`，等待完成後切換至「技術分析圖表」頁籤，驗證 ECharts 綜合技術指標圖表是否能精美呈現、且滑動 DataZoom 縮放功能正常運作。

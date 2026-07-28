# 完成後的檢查與驗證指南 (inspection_checklist.md)

本文件提供了在部署與開發台股搜尋、儲存與背景排程模組後，如何執行系統性的健康檢查、功能驗證與常見錯誤排查。

---

## 📋 1. 功能檢核清單 (Checklist)

| 檢驗項目 | 檢查要點與標準 | 驗證操作步驟 |
| :--- | :--- | :--- |
| **1. 路由分開驗證** | `/profile/` 網頁無 Tabs 切換，僅顯示台股基本資料；`/tech-stack/` 無 Tabs 切換，僅顯示健康監控。 | 造訪 [http://localhost/profile/](http://localhost/profile/) 與 [http://localhost/tech-stack/](http://localhost/tech-stack/) |
| **2. 自動刷新消除** | 在任一路徑下，打開網頁均不會發生每秒一次的反覆重新整理 (Full Page Reload) 循環。 | 檢視瀏覽器 Console 或是 network 請求 |
| **3. 靜態/動態更新** | `/profile/` 載入時不執行請求，僅在按按鈕才更新。`/tech-stack/` 每 10 分鐘自動檢查。 | 檢視頁面上之說明字樣與 network 發起的請求 |
| **4. 雙重輪詢防空與再次抓取** | 點擊「即時更新並儲存」後，前台進入載入，待 Profile 與技術分析資料皆落庫完後才停止輪詢，並自動重新載入展示 ECharts 技術指標圖表與股價看板。 | 輸入 `2330` 並點擊「⚡ 即時更新並儲存」 |
| **5. 台灣時區 (UTC+8) 對齊** | 新聞發布時間與 API 時間回傳皆正確顯示為台北本地時間。 | 檢查戰情室新聞發布時間與 Datatable 內的時間格式 |
| **6. DataTables 分頁功能** | 點擊重大行事曆與新聞公告區的 `MORE +` 按鈕，能在新分頁渲染出搭載 DataTables 分頁、搜尋與深色客製化樣式的清單。 | 點擊 More 按鈕，確認新分頁載入正常 |
| **7. 12pt 最小字體限制** | 網頁上所有細小字體（包括 DataTables 分頁按鈕與前台小標題）最小不小於 12pt (16px)。 | 檢查前台各小字體區塊之 CSS 計算屬性 |
| **8. Unfold 管理後台** | 左側選單具備台股 profile 的四個 Model 資料表；且 `Periodic tasks` 自動配置為每 4 小時一次。 | 登入後台 [http://localhost/admin/](http://localhost/admin/) (帳密: `admin`/`adminpassword123`) |
| **9. 單元測試健康** | 股票模組的單元測試全數跑過 (4 項測試 OK)。 | 於宿主機執行 `docker compose exec fin-backend python manage.py test stock_db` |

---

## 🧪 2. 單元測試與自動化驗證指令

### 執行單元測試
```bash
# 執行 stock_db 模組全套單元測試
docker compose exec fin-backend python manage.py test stock_db
```
* **預期輸出**：`Ran 4 tests in 0.042s ... OK`。

### 執行自動化健康檢測
```bash
# 執行專案自定義健康測試腳本
./scripts/test_health.sh
```
* **預期輸出**：`🎉 所有自動化健康測試均完全通過!`。

---

## 🐞 3. 常見錯誤與排查步驟 (Troubleshooting)

### 1. 頁面一直 reload (自動刷新)
* **原因**：Vite 的 HMR WebSocket 斷線或是 base URL pathname 不匹配，觸發 Vite 客戶端的安全重試機制。
* **排查與解法**：確認 [vite.config.ts](file:///home/dengkai/projects/financial-information/frontend/vite.config.ts) 中，`server.hmr` 已被設為 `false`，且已執行 `docker compose restart fin-frontend`。

### 2. 即時更新後技術分析圖表一片空白
* **原因**：輪詢機制太早結束（在技術分析資料計算寫入完成前，只要 profile 寫入就返回了 True）。
* **排查與解法**：
  * 確認 [views.py](file:///home/dengkai/projects/financial-information/backend/core/views.py) 的本地查詢模式中，包含了 `profile` 和 `TechnicalAnalysis` (has_ta) 存在性的雙重檢查。
  * 確認 [App.vue](file:///home/dengkai/projects/financial-information/frontend/src/App.vue) 的輪詢回調中，有調用 `await handleStockSearch(false)` 重新加載數據。

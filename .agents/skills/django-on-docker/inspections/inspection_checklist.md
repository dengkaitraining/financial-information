# 完成後的檢查與驗證指南 (inspection_checklist.md)

本文件提供了在部署與開發台股搜尋、儲存與背景排程模組後，如何執行系統性的健康檢查、功能驗證與常見錯誤排查。

---

## 📋 1. 功能檢核清單 (Checklist)

| 檢驗項目 | 檢查要點與標準 | 驗證操作步驟 |
| :--- | :--- | :--- |
| **1. 路由分開驗證** | `/profile/` 網頁無 Tabs 切換，僅顯示台股基本資料；`/tech-stack/` 無 Tabs 切換，僅顯示健康監控。 | 造訪 [http://localhost/profile/](http://localhost/profile/) 與 [http://localhost/tech-stack/](http://localhost/tech-stack/) |
| **2. 自動刷新消除** | 在任一路徑下，打開網頁均不會發生每秒一次的反覆重新整理 (Full Page Reload) 循環。 | 檢視瀏覽器 Console 或是 network 請求 |
| **3. 靜態/動態更新** | `/profile/` 網載入時完全不執行任何請求，只有按按鈕才更新。`/tech-stack/` 載入時會自動執行 1 次，爾後每 10 分鐘自動定時檢查。 | 檢視頁面上之說明字樣與 network 發起的請求 |
| **4. 異步更新與落庫** | `/profile/` 點擊「即時更新並儲存」後，能立即提示任務啟動並在數秒後動態渲染出台積電的 25 欄位資料。 | 輸入 `2330` 並點擊「⚡ 即時更新並儲存」 |
| **5. More 詳情頁面** | 點擊重大行事曆與新聞公告區的 `MORE +` 按鈕，能在新分頁渲染出對應股票的全部內容。 | 點擊 More 按鈕，確認新分頁載入正常 |
| **6. Unfold 管理後台** | 左側選單具備台股 profile 的四個 Model 資料表；且 `Periodic tasks` 能正常載入與編輯。 | 登入後台 [http://localhost/admin/](http://localhost/admin/) (帳密: `admin`/`adminpassword123`) |
| **7. 單元測試健康** | core app 的單元測試全數跑過 (10 項測試 OK)。 | 於宿主機執行 `docker compose exec fin-backend python manage.py test core` |

---

## 🧪 2. 單元測試與自動化驗證指令

### 執行單元測試
```bash
# 執行 core 模組全套單元測試 (含 ORM 欄位約束、API 查詢、Mock即時爬蟲更新與詳情渲染)
docker compose exec fin-backend python manage.py test core
```
* **預期輸出**：`Ran 10 tests in 0.146s ... OK`。

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

### 2. 即時更新時發生 502 / 504 錯誤或是卡死逾時
* **原因**：沒有使用非同步，或是 GNews 爬蟲對每筆新聞執行了無謂的 Google 翻譯。
* **排查與解法**：
  * 確認 [views.py](file:///home/dengkai/projects/financial-information/backend/core/views.py) 的 `update_mode` 已使用 `update_single_stock.delay(stock_id)` 進行異步任務派發，而非在 view 中同步調用 scraper。
  * 確認 [fetcher.py](file:///home/dengkai/projects/financial-information/backend/core/scraper/fetcher.py) 已移除新聞標題和摘要的 `self.translator.translate` 翻譯調用。

### 3. Celery 任務沒有執行（資料庫沒有寫入）
* **原因**：Celery Worker 容器因為被 `entrypoint.sh` 中的 `runserver` 覆蓋而沒有真正執行 Celery 服務。
* **排查與解法**：
  * 確認 [entrypoint.sh](file:///home/dengkai/projects/financial-information/backend/entrypoint.sh) 的最後一行支援 `exec "$@"` 自定義指令傳入。
  * 執行 `docker compose ps` 確認 `fin_celery_worker` 與 `fin_celery_beat` 狀態皆為 `Up`。
  * 執行 `docker compose logs fin-celery-worker` 檢視 Worker 中是否成功列出 `[tasks]` 清單並有收到 `Task core.tasks.update_single_stock received` 日誌。

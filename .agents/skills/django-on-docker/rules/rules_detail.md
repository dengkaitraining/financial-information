# Django on Docker 準則細部資訊 (Rules)

本檔案詳細記錄維護與開發本專案時必須嚴格遵守的規範與準則。

---

## 規範與原則對照表

| 規範項目 | 說明與要求基準 | 套用對象 / 檔案 | 使用時機與維護原則 |
| :--- | :--- | :--- | :--- |
| **全專案繁體中文註解** | 所有代碼與設定檔需具備詳細繁體中文說明 | `.py`, `.ts`, `.vue`, `.sh`, `.yaml`, `.cnf`, `.conf`, `.env`, `Dockerfile` | 新增或修補程式與設定檔時 |
| **多連線與多資料庫** | 支持 `user_stock` (`user_stock_db`) 與 `user_employee` (`db_employee`) | `.env`, `init_multi_db.sql`, `settings.py` | 設定多資料庫存取與帳號權限隔離時 |
| **群組權限控制** | `Database Managers` 群組與 `can_manage_db_tables` 權限管轄 | `core/models.py`, `entrypoint.sh` | 進行進階資料庫管理員 `/admin/db-manager/` 控制時 |
| **跨平台 LF 換行符號** | 強制使用 Unix `LF` 換行格式，防範 Windows 換行錯亂 | `*.sh`, `docker-compose.yaml`, `Dockerfile` | Git checkout 與腳本執行時 (由 [.gitattributes](../../../.gitattributes) 強制) |
| **實體 Volume 掛載** | 使用相對路徑 `./db_data` 與 `./redis_data` | `docker-compose.yaml` (db, redis) | 容器持久化資料庫與快取數據時 |
| **Vite 檔案輪詢機制** | 啟用 `watch: { usePolling: true }` 機制 | `frontend/vite.config.ts` | 於宿主機 (Windows/Linux) 開發熱更新 (HMR) 時 |
| **手動測試資料隱蔽** | 藉由 `SHOW_BACKEND_VER` 參數控制手動測試輸出，正式環境 (False) 下隱蔽敏感資料 | `backend/backend_ver/` | 執行手動測試驗證腳本時 |

---

## URL 路由與回應規範對照表

| 請求網址 (URL) | 轉接目標 (Target Container) | 預期回應內容 / 處理機制 | 權限管制要求 |
| :--- | :--- | :--- | :--- |
| **`http://localhost/`** | Django Backend (`/`) | 純文字：`Django + Vue.js Web 資訊系統開發環境的服務已啟用。` | 無需權限 |
| **`http://localhost/tech-stack/`** | Vue 3.5 Frontend (`/tech-stack/`) | Vue 3.5 儀表板 (含 10 分鐘 `600,000 ms` 定時自動檢查) | 無需權限 |
| **`http://localhost/admin/`** | Django Backend (`/admin/`) | Django Unfold 現代化管理介面 (資料存於 MariaDB `auth_user` 與 `employees`) | Staff / Admin |
| **`http://localhost/admin/db-manager/`** | Django Backend (`db_manager`) | 資料庫與表單管理員 (帳號切換/SHOW DATABASES/SHOW GRANTS/DataTables CRUD) | `can_manage_db_tables` 權限 |
| **`http://localhost/api/status/`** | Django Backend (`/api/status/`) | JSON 數據 (對 MariaDB 執行 `SELECT 1` 檢測與 Redis 寫入測試) | 無需權限 |

---

## 相關文件連結
- 返回主要技能規範：[SKILL.md](../SKILL.md)
- 指定工具細部資訊：[tools.md](../scripts/tools.md)
- 逐步解說細部資訊：[walkthrough_details.md](../references/walkthrough_details.md)

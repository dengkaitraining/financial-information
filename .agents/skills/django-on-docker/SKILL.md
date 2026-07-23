---
name: django-on-docker
description: 提供基於 Docker Compose 容器化技術之 Python Django 5.2 LTS、Vue.js 3.5、MariaDB 12.3 (多連線帳號/多資料庫/實體目錄掛載 ./db_data)、Redis 8.8 與 Apache HTTPD 多容器開發環境建立、管理、維護、Host OS 自動判斷 (Windows/Linux/macOS)、單元測試與自動化部署指南。
---

# Django on Docker 容器化 Web 資訊系統開發 Skill

## 1. 角色定位 (Role)
您是 **Django on Docker 容器化系統架構專家**，負責維護與管理包含 Apache HTTPD 反向代理伺服器、MariaDB 12.3 多關聯式資料庫 (支援 `user_stock` 與 `user_employee` 多帳號權限隔離、跨庫存取與實體目錄 `./db_data` 掛載)、Redis 8.8 快取與 Session 伺服器 (掛載 `./redis_data`)、Django 5.2 LTS (整合 Django Unfold 後台、Host OS 自動判斷與單元測試套件) 與 Vue 3.5 (整合 TypeScript 與 Tailwind CSS v4.3 效能引擎) 之多容器技術堆疊。

### 技術堆疊與組件對照表

| 組件名稱 | 技術堆疊與版本 | 服務角色與用途 | 使用時機與存取點 |
| :--- | :--- | :--- | :--- |
| **`init-dir`** | Alpine Linux + Shell | 目錄建立與 Host OS (Win/Linux/Mac) 自動權限修復 | 容器編排優先執行，修復完成即退出 |
| **`web`** | Apache HTTPD 2.4-alpine | 反向代理網頁伺服器，統一 Port 80 進入點 | 處理 `/tech-stack/`, `/`, `/admin/`, `/api/` |
| **`backend`** | Python 3.11 + Django 5.2 LTS | 後端網頁框架、Unfold 美觀後台、REST API 與單元測試 | 提供純文字、Unfold、`employees` 管理 API 與 9 項單元測試 |
| **`backend_ver`** | Python 3.11 + 驗證腳本 | 後端程式、模組手動測試驗證環境，包含多資料庫路由與 Redis 快取 | 進入 `fin_django_backend` 執行 `python backend_ver/run_all.py` |
| **`frontend`** | Vue 3.5 + TS + Tailwind v4.3 | 前端 SPA 開發伺服器 (Vite `base: /tech-stack/`) | 造訪 `http://localhost/tech-stack/` 儀表板 (含 10 分鐘自動檢測) |
| **`db`** | MariaDB 12.3 | 多關聯式 SQL 資料庫 (`user_stock_db`, `db_employee`) | 提供 `user_stock` 與 `user_employee` 多帳號權限管理，掛載 `./db_data` |
| **`redis`** | Redis 8.8 | 快取與 Session 高併發記憶體資料庫 (掛載 `./redis_data`) | 處理 Django 高併發 Session 與快取資料存取 |
| **`scripts`** | Shell & PowerShell | 跨平台一鍵自動化部署與單元測試作業腳本 | 執行 `scripts/deploy.sh` (Linux/Mac/WSL) 或 `deploy_windows.ps1` |

---

## 2. 準則 (Rules)
準則細部資訊與規範說明，請參閱相對路徑文件：
[rules_detail.md](./rules/rules_detail.md)

## 3. 指定工具 (Tools)
指定工具細部資訊與指令範例，請參閱相對路徑文件：
[tools.md](./scripts/tools.md)

## 4. 逐步解說 (Walkthrough)
逐步解說項目細部資訊、架構圖與運作流程，請參閱相對路徑文件：
[walkthrough_details.md](./references/walkthrough_details.md)

## 5. 完成後的檢查 (Final Inspection)
完成後的檢核項目、測試步驟與驗證基準，請參閱相對路徑文件：
[inspection_checklist.md](./inspections/inspection_checklist.md)

## 6. 任務日誌紀錄 (Task Logs)
- [01_implementation_plan.md](./task_logs/01_implementation_plan.md)
- [02_task_list.md](./task_logs/02_task_list.md)
- [03_walkthrough.md](./task_logs/03_walkthrough.md)

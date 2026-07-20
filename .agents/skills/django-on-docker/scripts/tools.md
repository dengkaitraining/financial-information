# Django on Docker 指定工具細部資訊 (Tools)

本文件詳細記載用於建置、管理、維護與自動化測試 Django on Docker 容器堆疊之指定工具與命令。

---

## 1. 工具與命令對照表

| 工具 / 指令名稱 | 類型與所在位置 | 主要功能與說明 | 使用時機與範例 |
| :--- | :--- | :--- | :--- |
| **`docker compose up --build -d`** | 容器編排工具 | 重新編譯 `web`, `backend`, `frontend` 映像檔，並以背景模式啟動全數容器 | 啟動或更新部署時 |
| **`python manage.py seed_employees`** | 種子資料產生指令 | 自動在 `db_employee` 資料庫之 `employees` 表生成 10 筆測試員工資料 | 資料庫初始化或測試時 |
| **`/admin/db-manager/api/crud/`** | DataTables CRUD API | 接收 POST JSON Payload，動態執行 SQL INSERT, UPDATE, DELETE 記錄操作 | DataTables 表單線上即時編輯時 |
| **`netcat-openbsd (nc)`** | 網路與健康等待工具 | 對 MariaDB 3306 Port 進行 TCP 健康輪詢，確認資料庫就緒 | `entrypoint.sh` 啟動 Migration 前 |
| **`./scripts/test_health.sh`** | 自動化測試腳本 | 自動測試根目錄純文字、API JSON 狀態、Vue 200 OK 與 `.env` 變數 | 建置完成後進行整合測試時 |

---

## 2. 自動化測試腳本說明 (`./scripts/test_health.sh`)

本專案提供獨立的自動化測試腳本，位於 [../../../scripts/test_health.sh](../../../scripts/test_health.sh)：

| 測試步驟 | 測試目標與網址 | 檢驗標準 / 回應條件 |
| :--- | :--- | :--- |
| **步驟 1** | 根目錄 `http://localhost/` | 是否包含文字 `Django + Vue.js Web 資訊系統開發環境` |
| **步驟 2** | API 端點 `http://localhost/api/status/` | JSON 資料庫 (`database`) 與快取 (`redis`) 狀態均為 `"connected"` |
| **步驟 3** | 儀表板頁面 `http://localhost/tech-stack/` | HTTP 狀態碼為 `200 OK` |
| **步驟 4** | 環境變數設定檔 `.env` | 是否設定 `DJANGO_DEBUG=True` 且 `DJANGO_ALLOWED_HOSTS` 包含 `localhost` 或 `*` |

---

## 相關文件連結
- 返回主要技能規範：[SKILL.md](../SKILL.md)
- 準則細部資訊：[rules_detail.md](../rules/rules_detail.md)
- 逐步解說細部資訊：[walkthrough_details.md](../references/walkthrough_details.md)

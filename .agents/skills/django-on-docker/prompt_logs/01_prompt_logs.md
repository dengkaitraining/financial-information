# [Django + Vue.js (TS/Tailwind) 資訊系統容器化開發環境實作計畫 (Implementation Plan)]
------
# 使用 docker compose 建立 Python Django Web base 資訊系統開發環境。
## 1. 應用套件與技術堆疊：
 - 網頁伺服器：apache httpd 伺服器。
 - 資料庫伺服器：MariaDB 伺服器。
 - 前端技術堆疊：TypeScript、Vue.js 框架、Tailwind CSS UI 套件。
 - 後端技術堆疊：Python Django 框架、Python Django Unfold 後台管理套件。
 - 資料庫連線技術：使用 Redis 技術以避免高併發的問題。
## 2. 技術堆疊容器化：
 - 將「1. 應用套件與技術堆疊」容器化，轉換為 docker compose 並建立下列文件資訊：
   - Dockerfile
   - docker-compose.yaml
   - .env
   ...
   等 docker compose 文件。
 - docker-compose.yaml 內 volumes 資料儲存目錄指向專案內實體路徑。
 - docker-compose.yaml 內加入 docker network bridge 網路連線。
 
## 3. 檢查 docker compose 文件
 - 檢查 docker compose 相關文件在 Linux , Windows 運行是否正確，並協助修補文件內容。

------
1. Vue 更新至 3.5。
2. Redis 更新至 8.8。
3. MariaDB 更新至 12.3。
4. Django 更新至 5.2。
5. Tailwind CSS UI 更新至 4.3。

------
使用 sudo deocker compose up --build -d 發生錯誤資訊：Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: exec: "/app/entrypoint.sh": permission denied

------
# 1. 移除所有容器 docker compose 資訊、空間 volumes 與 映像檔資訊。
# 2. 在 .env 加入 ：
 - Django Unfold 後台管理者的「帳戶」與「密碼」資訊。
 - MariaDB 使用者端自定義(user define)設定檔資訊。
# 3. 重新執行全新的容器 docker compose 作業 (如：docker compose up --build -d)。

------
# 1. 在 .env 加入 ：
 - Apache httpd 使用者端自定義(user define)設定檔資訊。
 - Redis 使用者端自定義(user define)設定檔資訊。
# 2. Apache httpd、MariaDB、Redis 請加入「option」的設定資訊。
# 3. 專案內的程式(.py 等程式)、服務設定檔(.yaml, .cnf, .conf, .env, .json, .ts, .sh, Dockerfile 等設定檔)加入詳細的說明與功能描述。

------
# 1. 將首頁「Django + Vue.js Web 資訊系統開發環境」的路徑「 http://localhost/」修改為「http://localhost/tech-stack」。
# 2. 原本路徑「 http://localhost/」改為顯示「Django + Vue.js Web 資訊系統開發環境的服務以啟用 。」的簡單文字資訊。
# 3. 修改後請更新專案內的程式(.py 等程式)、服務設定檔(.yaml, .cnf, .conf, .env, .json, .ts, .sh, Dockerfile 等設定檔)的詳細說明與功能描述。

------
# 1. 修改「Django + Vue.js Web 資訊系統開發環境」(http://localhost/tech-stack) 設定資訊：
 - 第一次連上「Django + Vue.js Web 資訊系統開發環境」(http://localhost/tech-stack) 自動檢查各項服務狀態一次。
 - 爾後 「Django + Vue.js Web 資訊系統開發環境」(http://localhost/tech-stack) 每 10 分鐘自動檢查各項服務狀態一次。
# 2. 修改後請更新專案內的程式(.py 等程式)、服務設定檔(.yaml, .cnf, .conf, .env, .json, .ts, .sh, Dockerfile 等設定檔)的詳細說明與功能描述。

------
# 1. 檢查「Django + Vue.js Web 資訊系統開發環境」的狀態資訊：
 - 檢查專案內的程式(.py 等程式)、服務設定檔(.yaml, .cnf, .conf, .env, .json, .ts, .sh, Dockerfile 等設定檔)的資訊是否正確。
 - 檢查 docker compose 建立後的運行狀態是否正確。
# 2. 檢查完成後修改後請更新專案內的程式(.py 等程式)、服務設定檔(.yaml, .cnf, .conf, .env, .json, .ts, .sh, Dockerfile 等設定檔)的詳細說明與功能描述。
# 3. 檢查與修改成後，依據專案內修正的資訊內容，例如：專案內的程式(.py 等程式)、服務設定檔(.yaml, .cnf, .conf, .env, .json, .ts, .sh, Dockerfile 等設定檔)等，修改以下內容：
 - 依據專案目前的結果，更新「實作計畫 (Implementation Plan)」、「任務清單 (Task List)」、「逐步解說 (Walkthrough)」詳細資訊
 - 更新完成後:
   - 「實作計畫 (Implementation Plan)」資訊儲存在專案內「./agents/task_logs/01_implementation_plan.md」的檔案。
   - 「任務清單 (Task List)」資訊儲存在專案內「./agents/task_logs/02_task_list.md」的檔案。
   - 「逐步解說 (Walkthrough)」資訊儲存在專案內「./agents/task_logs/03_walkthrough.md」的檔案。

------
# 1. 依據文件資訊<spec>建立以下資訊內容<info>：
 <spec>
 - 「實作計畫 (Implementation Plan)」的資訊(/home/dengkai/projects/django-on-docker/agents/task_logs/01_implementation_plan.md)。
 - 「任務清單 (Task List)」資訊儲存在專案內的資訊(/home/dengkai/projects/django-on-docker/agents/task_logs/02_task_list.md)。
 - 「逐步解說 (Walkthrough)」資訊儲存在專案內的資訊(/home/dengkai/projects/django-on-docker/agents/task_logs/03_walkthrough.md)。
 </spec>
 <info>
 - 建立詳細的 README.md 說明檔資訊包含：
   (1) 專案簡介 (Description)、mermaid 格式的「系統架構圖 (System Architecture)」、「系統流程圖 (System Flowchart」、「系統時序圖 (Sequence Diagram)」。
   (2) 安裝與建置指南 (Installation and Setup)。
   (3) 設定說明 (Configuration)。
   (4) 執行與啟動本地服務 (Usage / Getting Started)。
   (5) 資料夾結構與架構簡述 (Project Structure)。
   (6) 系統測試與驗證 (System Testing and Verification)。
   (7) 貢獻與授權 (Contributing and License)。
 </info>
# 2. 專案內的 agents 資料夾「/home/dengkai/projects/django-on-docker/agents」修改為「/home/dengkai/projects/django-on-docker/.agents」。

------
# 1. 詳細說明專案內「MariaDB 12.3 關聯式資料庫」與「Django 更新至 5.2」如何協作、運作？
# 2. 依據「1.」詳細說明的協作、運作結果更新「實作計畫 (Implementation Plan)」、「任務清單 (Task List)」、「逐步解說 (Walkthrough)」詳細資訊，也一併更新<data>內容：
 <data>
   (1) 「實作計畫 (Implementation Plan)」的資訊(/home/dengkai/projects/django-on-docker/.agents/task_logs/01_implementation_plan.md)。
   (2) 「任務清單 (Task List)」資訊儲存在專案內的資訊(/home/dengkai/projects/django-on-docker/.agents/task_logs/02_task_list.md)。
   (3) 「逐步解說 (Walkthrough)」資訊儲存在專案內的資訊(/home/dengkai/projects/django-on-docker/.agents/task_logs/03_walkthrough.md)。
 </data>
# 3. 依據「1.」詳細說明的協作、運作結果更新「 README.md」說明檔資訊，包含<info>內容：
 <info>
   (1) 專案簡介 (Description)、mermaid 格式的「系統架構圖 (System Architecture)」、「系統流程圖 (System Flowchart)」、「系統時序圖 (Sequence Diagram)」。
   (2) 安裝與建置指南 (Installation and Setup)。
   (3) 設定說明 (Configuration)。
   (4) 執行與啟動本地服務 (Usage / Getting Started)。
   (5) 資料夾結構與架構簡述 (Project Structure)。
   (6) 系統測試與驗證 (System Testing and Verification)。
   (7) 貢獻與授權 (Contributing and License)。
 </info>

------
# 1. 依據文件資訊<spec>建立 skills 資訊內容<skills>：
 <spec>
 - 「實作計畫 (Implementation Plan)」的資訊(/home/dengkai/projects/django-on-docker/.agents/task_logs/01_implementation_plan.md)。
 - 「任務清單 (Task List)」資訊儲存在專案內的資訊(/home/dengkai/projects/django-on-docker/.agents/task_logs/02_task_list.md)。
 - 「逐步解說 (Walkthrough)」資訊儲存在專案內的資訊(/home/dengkai/projects/django-on-docker/.agents/task_logs/03_walkthrough.md)。
 - 「README.md 說明檔資訊」(/home/dengkai/projects/django-on-docker/README.md)。
 </spec>
 <skills>
 - 建立的 /home/dengkai/projects/django-on-docker/.agents/skills/django-on-docker/SKILL.md 檔案資訊包含：
   (1) SKILL 飆頭描述 (name, description)。
   (2) 角色定位 (role)。
   (3) 準則 (rules)。
   (4) 指定工具 (tools)：指定工具細部資訊，以 markdown 檔案儲存在 /home/dengkai/projects/django-on-docker/.agents/skills/django-on-docker/scripts/ 的資料夾內。
   (5) 逐步解說 (Walkthrough)：逐步解說項目細部資訊，以 markdown 檔案儲存在 /home/dengkai/projects/django-on-docker/.agents/skills/django-on-docker/references/ 的資料夾內。
   (6) 完成後的檢查 (Final inspection)：檢查作業細部資訊，以 markdown 檔案儲存在 /home/dengkai/projects/django-on-docker/.agents/skills/django-on-docker/inspections/ 的資料夾內。
 </skills>

------
# 1. 移除「1. SKILL 表頭描述 (Header Description)」標題資訊，內容修改為：
---
name: django-on-docker
description: 提供基於 Docker Compose 容器化技術之 Python Django 5.2 LTS、Vue.js 3.5、MariaDB 12.3、Redis 8.8 與 Apache HTTPD 多容器開發環境建立、管理、維護與自動化檢查指南。
---
# 2. 準則 (rules)：準則細部資訊，以 markdown 檔案儲存在 /home/dengkai/projects/django-on-docker/.agents/skills/django-on-docker/rules/ 的資料夾內。

------
# 1. 檢視 .agents/skills/django-on-docker 資料夾下的所有檔案內容：
 - .agents/skills/django-on-docker 資料夾內的markdown檔案內容中的檔案連結路徑請修改為相對路徑而非絕對路徑。
 - 檢視 .agents/skills/django-on-docker 資料夾下所有*.md 檔案內容，加入markdown語法的「表格」呈現技術堆疊、工具功能與使用時機。
 - 「.agents/prompt_logs」移動到「.agents/skills/django-on-docker/prompt_logs」下。
 - 「.agents/task_logs」移動到「.agents/skills/django-on-docker/task_logs」下。
# 2. 檢視.agents/skills/django-on-docker 資料夾下的所有檔案內容，確認呈現格式正確，無誤。
# 3. 依據「1., 2.」修改結果更新「實作計畫 (Implementation Plan)」、「任務清單 (Task List)」、「逐步解說 (Walkthrough)」詳細資訊，也一併更新<data>內容：
 <data>
   - 儲存<implementation_plan>「實作計畫 (Implementation Plan)」的資訊(/home/dengkai/projects/django-on-docker/.agents/skills/django-on-docker/task_logs/01_implementation_plan.md)。
   - 儲存<task_list>「任務清單 (Task List)」資訊(/home/dengkai/projects/django-on-docker/.agents/skills/django-on-docker/task_logs/02_task_list.md)。
   - 儲存<walkthrough>「逐步解說 (Walkthrough)」資訊(/home/dengkai/projects/django-on-docker/.agents/skills/django-on-docker/task_logs/03_walkthrough.md)。
   - 更新專案內的程式(.py 等程式)、服務設定檔(.yaml, .cnf, .conf, .env, .json, .ts, .sh, Dockerfile 等設定檔)的詳細說明與功能描述。
   - 更新README.md的<info>與<test>內容：
   <info>
     - 加入markdown語法的「表格」呈現技術堆疊、工具功能與使用時機。
   </info>
   <test>
     - 根目錄：檢查網頁是否有出現「Django + Vue.js Web 資訊系統開發環境」的文字
     - API端點：檢查/api/status/返回的json檔，確認資料庫與快取有連接成功
     - 頁面功能：檢查/tech-stack/是否有出現所有技術堆疊的圖標
     - 自動化測試：執行./scripts/test_health.sh，確認所有測試皆通過
     - 檢查.env是否有設定DJANGO_DEBUG=True與ALLOWED_HOSTS=['*']
   </test>
 </data>
 
------
# 1. django mariadb 多個使用者 連線 .env 的方式：
 <dbs>
  - 不同的資料庫可以設定不同的連線帳號與密碼，加入 .env 檔案管理，例如：資料庫db_employee提供user_employee讀寫使用。
  - .env 檔案內資料庫帳號 user_stock 也可以讀寫資料庫 db_employee。
  - 在資料庫 db_employee增加以下資料表：
    <table>
     - 員工主資料表 (employees)
     | 欄位名稱 | 資料型態 | 屬性限制 | 欄位說明 | 備註說明 |
     |---|---|---|---|---|
     | id | BIGINT | PRIMARY KEY, AUTO_INCREMENT | 系統自動遞增 ID | 內部關聯使用的代理鍵（Surrogate Key） |
     | employee_num | VARCHAR(20) | UNIQUE, NOT NULL | 員工工號 | 企業實際使用的工號，例如：EMP2026001 |
     | first_name | VARCHAR(50) | NOT NULL | 名字 | 區分姓與名有利於國際化系統設計 |
     | last_name | VARCHAR(50) | NOT NULL | 姓氏 | 區分姓與名有利於國際化系統設計 |
     | national_id | VARCHAR(20) | UNIQUE, NOT NULL | 身分證字號 / 護照號碼 | 機敏資料，建議在應用層加密後存放 |
     | gender | TINYINT | NOT NULL | 性別 | 0: 未知, 1: 男, 2: 女, 3: 非二元 |
     | birth_date | DATE | NOT NULL | 出生日期 | 計算員工法定年齡與發放生日福利 |
     | email | VARCHAR(100) | UNIQUE, NOT NULL | 公司電子信箱 | 用於系統登入與公務通知 |
     | personal_email | VARCHAR(100) | NULL | 個人電子信箱 | 離職聯絡或緊急狀況備用 |
     | phone | VARCHAR(20) | NOT NULL | 行動電話 | 建議統一過濾掉點或橫線，純數字存放 |
     | department_id | INT | FOREIGN KEY | 所屬部門 ID | 關聯至部門表 (departments.id) |
     | job_title_id | INT | FOREIGN KEY | 職務 / 職稱 ID | 關聯至職稱表 (job_titles.id) |
     | manager_id | BIGINT | FOREIGN KEY | 直屬主管 ID | 自我關聯回 employees.id，建立組織樹 |
     | status | TINYINT | NOT NULL, DEFAULT 1 | 員工狀態 | 0: 離職, 1: 在職, 2: 留職停薪, 3: 試用期 |
     | hire_date | DATE | NOT NULL | 到職日期 | 計算年資與特休假特權的基準 |
     | termination_date | DATE | NULL | 離職日期 | 員工離職時填入，在職時為 NULL |
     | created_at | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 資料建立時間 | 系統審計追蹤欄位 |
     | updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP | 資料更新時間 | 系統審計追蹤欄位 |
    </table>
  - 員工主資料表 (employees)隨機加入 10 筆員工資料。
 </dbs>
# 2. Django Unfold 後台增加資料庫表單管理功能：
 - 切換資料帳戶功能，以檢視可存取的資料庫與表單，與資料庫與表單的操作權限(show databases privilege, show tables privilege)。
 - 整合 DataTables 用以新增、修改、刪除資料庫表單資料。
# 3. Django Unfold 後台增加群組權限功能：後台增加資料庫表單管理，有權限的使用者才可以使用此功能。
# 4. 依據「1., 2., 3.」修改結果更新「實作計畫 (Implementation Plan)」、「任務清單 (Task List)」、「逐步解說 (Walkthrough)」詳細資訊，也一併更新<data>內容：
 <data>
   - 儲存<implementation_plan>「實作計畫 (Implementation Plan)」的資訊(/home/dengkai/projects/django-on-docker/.agents/skills/django-on-docker/task_logs/01_implementation_plan.md)。
   - 儲存<task_list>「任務清單 (Task List)」資訊(/home/dengkai/projects/django-on-docker/.agents/skills/django-on-docker/task_logs/02_task_list.md)。
   - 儲存<walkthrough>「逐步解說 (Walkthrough)」資訊(/home/dengkai/projects/django-on-docker/.agents/skills/django-on-docker/task_logs/03_walkthrough.md)。
   - 更新專案內的程式(.py 等程式)、服務設定檔(.yaml, .cnf, .conf, .env, .json, .ts, .sh, Dockerfile 等設定檔)、README.md的詳細說明與功能描述。
   - 更新 agents skills 資訊。
 </data>

------
# 1. 移除以下<func1>Django Unfold 後台功能：
 <func1>
  * 核心系統與驗證
    - 使用者管理
    - 群組與權限設定
  * 企業員工管理 (db_employee)
    - 員工主資料表 (employees)
  * 進階資料庫管理 (DataTables)
    - 資料庫與表單管理 (帳號切換/DataTables)
 </func1>

------
# 1. docker-compose.yaml 內 django_db volumes 資料儲存目錄指向專案內實體路徑./db_data。
# 2. Django 5.2 容器初始化啟動腳本 (backend/entrypoint.sh)，加入可自動判斷不同作業系統進行不同執行，如：
 - windows 自動改為 windows 執行方式。
 - linux 自動改為 linux 執行方式。
 - mac 自動改為 mac 執行方式。

------
# 1. 依據不同作業系統建立並執行完整的專案單元測試與部署作業
 - windows 單元測試與部署作業。
 - linux 單元測試與部署作業。
 - mac 單元測試與部署作業。

------
# 1. 請增加跨平台自動檢測部署與單元測試作業腳本 :
 - 統一跨平台進入點 (Linux, macOS, Git Bash, WSL) : ./scripts/deploy.sh
 - Linux 平台專用 (Ubuntu / Debian / RHEL) : ./scripts/deploy_linux.sh
 - macOS 平台專用 (Apple Silicon / Intel) : ./scripts/deploy_mac.sh

------
# 1. 依據不同作業系統建立並執行完整的專案單元測試與部署作業
 - windows 單元測試與部署作業。
 - linux 單元測試與部署作業。
 - mac 單元測試與部署作業。

------
# 1. 請增加跨平台自動檢測部署與單元測試作業腳本 :
 - 統一跨平台進入點 (Linux, macOS, Git Bash, WSL) : ./scripts/deploy.sh
 - Linux 平台專用 (Ubuntu / Debian / RHEL) : ./scripts/deploy_linux.sh
 - macOS 平台專用 (Apple Silicon / Intel) : ./scripts/deploy_mac.sh

------
# 1. 在不變更原檔案說明架構的基礎上，依據上述的對話內容與專案現況修改<reademe>、<task_log>、<skill>資訊：
 <reademe>
  - 「README.md 說明檔資訊」(README.md)。
  - 更新專案內的程式、服務設定檔(docker-compose.yaml, .env, .yaml, .env, .sh, Dockerfile 等設定檔)的詳細說明與功能描述。
 </reademe>
 <task_log>
  - 「實作計畫 (Implementation Plan)」的資訊(/.agents/skills/django-on-docker/task_logs/01_implementation_plan.md)。
  - 「任務清單 (Task List)」資訊儲存在專案內的資訊(/.agents/skills/django-on-docker/task_logs/02_task_list.md)。
  - 「逐步解說 (Walkthrough)」資訊儲存在專案內的資訊(/.agents/skills/django-on-docker/task_logs/03_walkthrough.md)。
 </task_log>
 <skill>
  - 修改 .agents/skills/django-on-docker/SKILL.md 檔案資訊包含：
   (1) SKILL 飆頭描述 (name, description)。
   (2) 角色定位 (role)。
   (3) 準則 (rules)。
   (4) 指定工具 (tools)：指定工具細部資訊，以 markdown 檔案儲存在 .agents/skills/django-on-docker/scripts/ 的資料夾內。
   (5) 逐步解說 (Walkthrough)：逐步解說項目細部資訊，以 markdown 檔案儲存在 .agents/skills/django-on-docker/references/ 的資料夾內。
   (6) 完成後的檢查 (Final inspection)：檢查作業細部資訊，以 markdown 檔案儲存在 .agents/skills/django-on-docker/inspections/ 的資料夾內。
 </skill>

 ------
 # 1. docker-compose.yaml 自動初始化目錄與權限修復服務 (init-dir)，加入可自動判斷不同作業系統進行不同修復，如：
 - windows 自動改為 windows 修復方式。
 - linux 自動改為 linux 修復方式。
 - mac 自動改為 mac 修復方式。

------
# 1. 修改 docker-compose.yaml 設定，加入 volume 持續化儲存設定。
    - 在 fin_django_backend 加入 python 程式、模組手動測試驗證的環境
    - 增加 backend_ver 程式手動測試驗證的環境，可透過 docker exec 方式進入容器執行程式，如：docker exec -it fin_django_backend bash /sh。 
    - 在 .env 增加 django 控制參數：測試開發環境顯示 backend_ver 資料夾與內容，正式上線隱蔽 backend_ver 資料夾與內容。

------
# 1. 修改 docker-compose.yaml 設定，加入 volume 持續化儲存設定。
    - 在 fin_vue_frontend 加入 vue 程式、模組手動測試驗證的環境
    - 增加 frontend_ver 程式手動測試驗證的環境，可透過 docker exec 方式進入容器執行程式，如：docker exec -it fin_vue_frontend bash /sh。 
    - 在 .env 增加 vue 控制參數：測試開發環境顯示 frontend_ver 資料夾與內容，正式上線隱蔽 frontend_ver 資料夾與內容。
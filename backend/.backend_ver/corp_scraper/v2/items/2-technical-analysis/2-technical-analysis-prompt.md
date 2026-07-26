
```markdown
# 請使用 python TwStock 與 yfinance 套件建構與Yahoo股市類似「個股技術分析 technical-analysis 資料」單元，詳細規格如<spec>。
<spec>
  1. 個股技術分析 technical-analysis 資料：
     - 成交量
     - KD,J
     - MACD
     - 乖離率
     - 威廉指標
     - 多空指標乖離
     - CDP
     - 動向指標DMI
  2. 依據「1.」資訊建立合適的表單與常用欄位，並生成 MariaDB 12.3 的 SQL create table 指令檔。
  3. 透過搜尋公司資訊的方式，抓取「1.」資訊並經使用者確認後，再分別將資料寫入「2.」建立表單資訊，並且確認各項「資料沒有重複」(MariaDB 12.3資料庫，資料庫名稱：stock_db)；並設定資料讀取的時間，如：1週、1個月、1季年等。、1年等。
  4. 寫入的公司股市技術分析資料，使用 ON DUPLICATE KEY UPDATE 機制，確保各項資料不會重複寫入；如果沒有抓取到公司股市技術分析資料，則不用寫入資料。
  5. yfinance 套件抓取到公司股市技術分析資料，使用 google translator for python 翻譯元件，將英文(en)翻譯為中文(zh-TW)。
  6. 使用 python mysqlclient 套件存取 MariaDB 資料庫。
  7. 最後產生 CLI 的測試界面，完整模組、(DB連線、存取)與測試程式分開成不同檔案，以確認 class 內各項功能正常運行。
</spec>

```
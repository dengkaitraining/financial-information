# ==============================================================================
# Django 後端服務 Dockerfile
# 說明：基於 Python 3.14 Slim 映像檔構建，安裝 C 編譯相依性與運作環境
# ==============================================================================

#FROM python:3.14-slim
#FinMind Python SDK 目前官方正式支援的最高版本為 Python 3.12
FROM python:3.12-slim

# 設定 Python 環境變數
# 防止 Python 產生 .pyc 暫存檔
ENV PYTHONDONTWRITEBYTECODE=1
# 強制 Python 標準輸出與標準錯誤直接即時印出 (不快取)
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 安裝 Linux 系統底層套件與 C 編譯器 (供 mysqlclient 與網路檢查套件編譯)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    netcat-openbsd \
    libxml2-dev \
    libxslt1-dev \
    #zlib1g-dev \
    #python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 升級 pip 與 wheel，確保能正確解析新版 CPython 的編譯標籤
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# 複製並升級 pip 與安裝 Python 相依套件
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# 複製容器啟動檔 entrypoint.sh 並賦予執行權限
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# 設定容器啟動進入點命令，顯式使用 sh 直譯器執行以防權限丟失
ENTRYPOINT ["sh", "/app/entrypoint.sh"]

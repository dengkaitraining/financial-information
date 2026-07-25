# ==============================================================================
# Apache HTTPD 反向代理服務 Dockerfile
# 說明：基於 Alpine Linux 構建輕量化 Apache HTTPD 網頁伺服器
# ==============================================================================

FROM httpd:2.4-alpine

# 設定環境變數
ENV LANG=zh_TW.UTF-8
ENV LANGUAGE=zh_TW:zh
#ENV LC_ALL=zh_TW.UTF-8
ENV TZ=Asia/Taipei

# 安裝時區與語系支援套件
RUN apk add --no-cache tzdata musl-locales musl-locales-lang

# 將自定義 HTTPD 代理設定檔複製至 Apache 設定目錄中
COPY httpd-custom.conf /usr/local/apache2/conf/httpd-custom.conf

# 在主設定檔 httpd.conf 結尾引入自定義設定檔
RUN echo "Include conf/httpd-custom.conf" >> /usr/local/apache2/conf/httpd.conf

# ==============================================================================
# Vue 3.5 前端開發服務 Dockerfile
# 說明：基於 Node 26 Alpine 輕量化環境，運行 Vite Dev Server
# ==============================================================================

FROM node:26-alpine

# 設定環境變數
ENV LANG=zh_TW.UTF-8
ENV LANGUAGE=zh_TW:zh
#ENV LC_ALL=zh_TW.UTF-8
ENV TZ=Asia/Taipei

RUN apk add --no-cache bash tzdata musl-locales musl-locales-lang

WORKDIR /app

# 複製 package.json 並安裝 Node.js 套件相依性
COPY package*.json ./
RUN npm install

# 複製前端原始碼
COPY . .

# 對外宣告 Port 5173
EXPOSE 5173

# 啟動 Vite 開發模式伺服器
CMD ["npm", "run", "dev"]

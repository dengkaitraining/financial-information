# [o] 2026-07-21 09:44
## error message:
### chromw browser 錯誤訊息：
```bash
Proxy Error
The proxy server could not handle the request
Reason: DNS lookup failure for: fin-backend
```

### apache_web 錯誤訊息：
```bash
[Tue Jul 21 01:25:38.341661 2026] [mpm_event:notice] [pid 1:tid 1] AH00489: Apache/2.4.68 (Unix) configured -- resuming normal operations
[Tue Jul 21 01:25:38.341770 2026] [core:notice] [pid 1:tid 1] AH00094: Command line: 'httpd -D FOREGROUND'
[Tue Jul 21 01:26:35.752031 2026] [proxy:error] [pid 11:tid 34] (EAI 3)Try again: [client 172.19.0.1:38042] AH00898: DNS lookup failure for: fin-backend returned by /
172.19.0.1 - - [21/Jul/2026:01:26:30 +0000] "GET / HTTP/1.1" 500 303
[Tue Jul 21 01:26:40.849374 2026] [proxy:error] [pid 11:tid 42] (EAI 3)Try again: [client 172.19.0.1:38052] AH00898: DNS lookup failure for: fin-backend returned by /favicon.ico, referer: http://localhost/
172.19.0.1 - - [21/Jul/2026:01:26:35 +0000] "GET /favicon.ico HTTP/1.1" 500 303
```

### backend 錯誤訊息：
```bash
nc: getaddrinfo for host "db" port 3306: Temporary failure in name resolution
  MariaDB 資料庫尚未就緒，等待 0.5 秒...。
```

## todo:
### apache_web 錯誤訊息正：
* 修改 ```file-[./apache/httpd-custom.conf]``` 設定資訊 ->
```ini
(**) {frontend:5173} -> {fin-frontend:5173}
(**) {backend:8000} -> {fin-backend:8000}
```

### backend 錯誤訊息修正：
* 修改 ```file-[./backend/entrypoint.sh]``` 設定資訊 ->
```ini
(50) {host = os.environ.get('DB_HOST', 'db')} -> {host = os.environ.get('DB_HOST', 'fin-db')}
```

### docker compose 啟動檔修改：
* 修改 ```file-docker-compose.yaml``` 設定資訊 ->
```yaml
# ==============================================================================
# Django + Vue.js Web 資訊系統 Docker Compose 多容器服務編排檔 (docker-compose.yaml)
# 說明：定義 6 大服務 (自動初始化權限修復 init-dir, Apache HTTPD, Vue 3.5, Django 5.2, MariaDB 12.3, Redis 8.8)
# ==============================================================================

services:
  # ----------------------------------------------------------------------------
  # 0. 初始化服務: 自動初始化目錄與權限修復服務 (init-dir)
  # ----------------------------------------------------------------------------
  fin-init-dir:
    image: alpine:latest
    container_name: fin_init_dir
    restart: "no"
    volumes:
      - .:/app
    environment:
      - HOST_OS=${HOST_OS:-auto}
    entrypoint: [ "/bin/sh", "/app/scripts/init_dir.sh" ]
    networks:
      fin-django-net:
        aliases:
          - init-dir

  # ----------------------------------------------------------------------------
  # 1. 網頁伺服器: Apache HTTPD 2.4 (反向代理)
  # ----------------------------------------------------------------------------
  fin-web:
    build:
      context: ./apache
      dockerfile: Dockerfile
    container_name: fin_apache_web
    restart: always
    ports:
      - "${HOST_WEB_PORT:-80}:80"
    volumes:
      - ${APACHE_CUSTOM_CONF:-./apache/httpd-custom.conf}:/usr/local/apache2/conf/httpd-custom.conf:ro
    command: [ "httpd-foreground" ]
    depends_on:
      - fin-backend
      - fin-frontend
    networks:
      fin-django-net:
        aliases:
          - web

  # ----------------------------------------------------------------------------
  # 2. 前端服務: Vue 3.5 + TypeScript + Tailwind CSS v4.3 (Vite 5)
  # ----------------------------------------------------------------------------
  fin-frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: fin_vue_frontend
    restart: always
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
    command: [ "npm", "run", "dev" ]
    depends_on:
      fin-init-dir:
        condition: service_completed_successfully
    networks:
      fin-django-net:
        aliases:
          - frontend

  # ----------------------------------------------------------------------------
  # 3. 後端服務: Python 3.11 + Django 5.2 LTS + Django Unfold
  # ----------------------------------------------------------------------------
  fin-backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: fin_django_backend
    restart: always
    volumes:
      - ./backend:/app
    env_file:
      - .env
    command: [ "sh", "/app/entrypoint.sh" ]
    depends_on:
      - fin-db
      - fin-redis
    networks:
      fin-django-net:
        aliases:
          - backend

  # ----------------------------------------------------------------------------
  # 4. 資料庫伺服器: MariaDB 12.3 (多資料庫與多帳號管理)
  # ----------------------------------------------------------------------------
  fin-db:
    image: mariadb:12.3
    #image: mariadb:10.11
    container_name: fin_django_db
    restart: always
    environment:
      MARIADB_DATABASE: ${DB_NAME:-user_stock_db}
      MARIADB_USER: ${DB_USER:-user_stock}
      MARIADB_PASSWORD: ${DB_PASSWORD:-user_stock_pass}
      MARIADB_ROOT_PASSWORD: ${DB_ROOT_PASSWORD:-db_root_secure_pass}
    ports:
      - "${HOST_DB_PORT:-3306}:3306"
    volumes:
      - ./db_data:/var/lib/mysql
      - ${MARIADB_CUSTOM_CONF:-./db_conf/my_custom.cnf}:/etc/mysql/conf.d/my_custom.cnf:ro
      - ./db_conf/init_multi_db.sql:/docker-entrypoint-initdb.d/init_multi_db.sql:ro
    command:
      - --character-set-server=utf8mb4
      - --collation-server=utf8mb4_unicode_ci
      - --max-connections=250
      - --default-storage-engine=InnoDB
    depends_on:
      fin-init-dir:
        condition: service_completed_successfully
    networks:
      fin-django-net:
        aliases:
          - db

  # ----------------------------------------------------------------------------
  # 5. 快取伺服器: Redis 8.8
  # ----------------------------------------------------------------------------
  fin-redis:
    image: redis:8.8
    #image: redis:alpine
    container_name: fin_django_redis
    restart: always
    ports:
      - "${HOST_REDIS_PORT:-6379}:6379"
    volumes:
      - ./redis_data:/data
      - ${REDIS_CUSTOM_CONF:-./redis_conf/redis.conf}:/usr/local/etc/redis/redis.conf:ro
    command: [ "redis-server", "/usr/local/etc/redis/redis.conf" ]
    depends_on:
      fin-init-dir:
        condition: service_completed_successfully
    networks:
      fin-django-net:
        aliases:
          - redis

# ------------------------------------------------------------------------------
# 橋接網路定義 (Bridge Network)
# ------------------------------------------------------------------------------
networks:
  fin-django-net:
    driver: bridge

```
<!-- ======================================================================= -->
<!-- Vue 3.5 主元件 (App.vue)                                                 -->
<!-- 說明：資訊系統開發環境儀表板 (路由存取點：http://localhost/tech-stack)     -->
<!-- 功能：首次開啟自動檢測 1 次，爾後每 10 分鐘 (600,000 ms) 定時自動重新檢測服務狀態 -->
<!-- ======================================================================= -->
<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

/**
 * 系統連線狀態 JSON 介面定義
 */
interface ServiceStatus {
  status: string
  django_version: string
  python_version: string
  database: {
    status: string
    error: string | null
    engine: string
    host: string
    name: string
  }
  redis: {
    status: string
    error: string | null
  }
}

// 響應式狀態變數
const loading = ref(true)
const error = ref<string | null>(null)
const backendData = ref<ServiceStatus | null>(null)
const lastCheckedTime = ref<string>('')

// 定義 10 分鐘自動檢測的間隔時間 (10 分鐘 = 600,000 毫秒)
const AUTO_REFRESH_INTERVAL_MS = 10 * 60 * 1000
let timerId: ReturnType<typeof setInterval> | null = null

/**
 * 向 Django 後端健康檢查 API (/api/status/) 發送請求
 */
const fetchStatus = async () => {
  loading.value = true
  error.value = null
  try {
    const res = await fetch('/api/status/')
    if (!res.ok) {
      throw new Error(`HTTP 錯誤! 狀態碼: ${res.status}`)
    }
    backendData.value = await res.json()
    // 記錄最後成功檢測時間
    const now = new Date()
    lastCheckedTime.value = now.toLocaleTimeString('zh-TW', { hour12: false })
  } catch (err: any) {
    console.error(err)
    error.value = err.message || '無法連線至 Django 後端 API'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // 1. 首次載入頁面時：給予 1.5 秒緩衝後，自動執行檢測 1 次
  setTimeout(fetchStatus, 1500)

  // 2. 爾後設定定時器：每 10 分鐘 (600,000 ms) 自動重新檢測各服務狀態
  timerId = setInterval(fetchStatus, AUTO_REFRESH_INTERVAL_MS)
})

onUnmounted(() => {
  // 元件卸載時清除定時器，防止記憶體洩漏
  if (timerId) {
    clearInterval(timerId)
  }
})
</script>

<template>
  <div class="min-h-screen bg-[#070b13] text-[#f3f4f6] flex flex-col items-center justify-between p-6 relative overflow-hidden select-none">
    
    <!-- 背景流光漸層光暈 -->
    <div class="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-900/10 rounded-full blur-[120px] pointer-events-none"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-cyan-900/10 rounded-full blur-[120px] pointer-events-none"></div>

    <!-- 主介面容器 -->
    <main class="w-full max-w-6xl z-10 flex-grow flex flex-col justify-center my-8">
      
      <!-- 頁頭標題區 -->
      <div class="text-center mb-10">
        <div class="inline-flex items-center space-x-2 bg-slate-900/60 border border-slate-800 px-4 py-1.5 rounded-full text-xs font-semibold tracking-wider text-cyan-400 uppercase mb-4 shadow-sm">
          <span>🐳 Docker Containerized Stack ( /tech-stack )</span>
        </div>
        <h1 class="text-4xl md:text-5xl font-extrabold tracking-tight bg-gradient-to-r from-white via-cyan-200 to-blue-400 bg-clip-text text-transparent drop-shadow-md">
          Django + Vue.js Web 資訊系統開發環境
        </h1>
        <p class="mt-3 text-base text-slate-400 max-w-3xl mx-auto">
          基於 Docker Compose 容器化技術，整合 Apache HTTPD 反向代理、MariaDB 12.3、Redis 8.8、Django 5.2 (Unfold) 與 Vue 3.5 (Tailwind v4.3)。
        </p>
        <!-- 定時檢測說明提示標籤 -->
        <div class="mt-4 inline-flex items-center space-x-2 bg-blue-950/40 border border-blue-800/40 px-3 py-1 rounded-full text-xs text-blue-300">
          <span class="relative flex h-2 w-2">
            <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
            <span class="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
          </span>
          <span>首次連線自動檢查 1 次 • 爾後每 10 分鐘自動重新檢測 1 次</span>
          <span v-if="lastCheckedTime" class="text-slate-400 border-l border-slate-700 pl-2 ml-1">上次檢測: {{ lastCheckedTime }}</span>
        </div>
      </div>

      <!-- 快捷操作卡片區 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        
        <!-- 卡片 1: Django Admin (含預設帳密提示) -->
        <a href="/admin/" target="_blank" class="glassmorphism p-6 rounded-2xl flex items-center justify-between group hover:border-cyan-500/30 transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg hover:shadow-cyan-950/20">
          <div class="flex items-center space-x-4">
            <div class="p-3 bg-teal-950/40 border border-teal-800/40 text-teal-400 rounded-xl group-hover:bg-teal-500/10 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
            </div>
            <div>
              <h3 class="font-bold text-slate-200">Django Unfold 後台</h3>
              <p class="text-xs text-teal-300 font-mono mt-0.5">帳號: admin | 密碼: (環境變數設定)</p>
            </div>
          </div>
          <div class="text-slate-500 group-hover:text-cyan-400 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </div>
        </a>

        <!-- 卡片 2: 健康檢查 API -->
        <a href="/api/status/" target="_blank" class="glassmorphism p-6 rounded-2xl flex items-center justify-between group hover:border-blue-500/30 transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg hover:shadow-blue-950/20">
          <div class="flex items-center space-x-4">
            <div class="p-3 bg-blue-950/40 border border-blue-800/40 text-blue-400 rounded-xl group-hover:bg-blue-500/10 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div>
              <h3 class="font-bold text-slate-200">健康檢查 JSON API</h3>
              <p class="text-xs text-slate-400 mt-0.5">檢視 MariaDB 與 Redis 連線數據</p>
            </div>
          </div>
          <div class="text-slate-500 group-hover:text-blue-400 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </div>
        </a>

        <!-- 卡片 3: 手動連線檢測 -->
        <button @click="fetchStatus" :disabled="loading" class="glassmorphism p-6 rounded-2xl flex items-center justify-between group hover:border-violet-500/30 transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg hover:shadow-violet-950/20 text-left w-full cursor-pointer">
          <div class="flex items-center space-x-4">
            <div class="p-3 bg-violet-950/40 border border-violet-800/40 text-violet-400 rounded-xl group-hover:bg-violet-500/10 transition-colors" :class="{ 'animate-spin': loading }">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 8H17" />
              </svg>
            </div>
            <div>
              <h3 class="font-bold text-slate-200">手動重新檢測</h3>
              <p class="text-xs text-slate-400 mt-0.5">{{ loading ? '檢測中...' : '立即重新測試各容器服務連線' }}</p>
            </div>
          </div>
          <div class="text-slate-500 group-hover:text-violet-400 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </button>

      </div>

      <!-- 容器服務節點狀態卡片區 -->
      <div class="grid grid-cols-1 md:grid-cols-5 gap-6">
        
        <!-- 1. Web Proxy (Apache HTTPD) -->
        <div class="glassmorphism p-6 rounded-2xl flex flex-col justify-between hover:border-orange-500/20 transition-all duration-300">
          <div>
            <div class="flex justify-between items-start mb-4">
              <span class="text-xs font-bold uppercase tracking-wider text-orange-400 bg-orange-950/40 px-2.5 py-1 rounded-md border border-orange-900/30">Apache</span>
              <span class="flex h-2.5 w-2.5 relative">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
            </div>
            <h2 class="text-xl font-bold text-slate-100">Apache HTTPD</h2>
            <p class="text-xs text-slate-400 mt-2 leading-relaxed">
              反向代理伺服器。對外監聽 Port 80，路由分配 /tech-stack、/admin 與 /。
            </p>
          </div>
          <div class="mt-6 pt-4 border-t border-slate-800/60 text-xs text-slate-500">
            <div>容器名稱: <span class="text-slate-300 font-mono">apache_web</span></div>
            <div class="mt-1">通訊埠: <span class="text-slate-300 font-mono">80:80</span></div>
          </div>
        </div>

        <!-- 2. Frontend (Vue 3.5) -->
        <div class="glassmorphism p-6 rounded-2xl flex flex-col justify-between hover:border-emerald-500/20 transition-all duration-300">
          <div>
            <div class="flex justify-between items-start mb-4">
              <span class="text-xs font-bold uppercase tracking-wider text-emerald-400 bg-emerald-950/40 px-2.5 py-1 rounded-md border border-emerald-900/30">Vue 3.5</span>
              <span class="flex h-2.5 w-2.5 relative">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
            </div>
            <h2 class="text-xl font-bold text-slate-100">Vue.js / Vite</h2>
            <p class="text-xs text-slate-400 mt-2 leading-relaxed">
              前端技術堆疊 (Base: /tech-stack/)。搭載 TypeScript 與 Tailwind CSS 4.3。
            </p>
          </div>
          <div class="mt-6 pt-4 border-t border-slate-800/60 text-xs text-slate-500">
            <div>框架版本: <span class="text-slate-300 font-mono">Vue v3.5</span></div>
            <div class="mt-1">樣式引擎: <span class="text-slate-300 font-mono">Tailwind v4.3</span></div>
          </div>
        </div>

        <!-- 3. Backend (Django 5.2) -->
        <div class="glassmorphism p-6 rounded-2xl flex flex-col justify-between hover:border-blue-500/20 transition-all duration-300" :class="{ 'border-rose-500/30': error }">
          <div>
            <div class="flex justify-between items-start mb-4">
              <span class="text-xs font-bold uppercase tracking-wider text-blue-400 bg-blue-950/40 px-2.5 py-1 rounded-md border border-blue-900/30">Django 5.2</span>
              <span class="flex h-2.5 w-2.5 relative">
                <span v-if="!loading && !error" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span :class="[loading ? 'bg-amber-500' : error ? 'bg-rose-500' : 'bg-emerald-500']" class="relative inline-flex rounded-full h-2.5 w-2.5"></span>
              </span>
            </div>
            <h2 class="text-xl font-bold text-slate-100">Django Backend</h2>
            <p class="text-xs text-slate-400 mt-2 leading-relaxed">
              Python 網頁框架。回應根路由 (/) 文字訊息，並處理 ORM 與 Unfold 後台。
            </p>
          </div>
          <div class="mt-6 pt-4 border-t border-slate-800/60 text-xs text-slate-500">
            <div>狀態: <span :class="[error ? 'text-rose-400' : 'text-slate-300']" class="font-semibold">{{ loading ? '檢查中...' : error ? '連線失敗' : '在線' }}</span></div>
            <div class="mt-1" v-if="backendData">版本: <span class="text-slate-300 font-mono">{{ backendData.django_version }}</span></div>
          </div>
        </div>

        <!-- 4. Database (MariaDB 12.3) -->
        <div class="glassmorphism p-6 rounded-2xl flex flex-col justify-between hover:border-cyan-500/20 transition-all duration-300" :class="{ 'border-rose-500/30': backendData && backendData.database.status !== 'connected' }">
          <div>
            <div class="flex justify-between items-start mb-4">
              <span class="text-xs font-bold uppercase tracking-wider text-cyan-400 bg-cyan-950/40 px-2.5 py-1 rounded-md border border-cyan-900/30">MariaDB 12.3</span>
              <span class="flex h-2.5 w-2.5 relative">
                <span v-if="backendData && backendData.database.status === 'connected'" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span :class="[loading ? 'bg-amber-500' : (backendData && backendData.database.status === 'connected') ? 'bg-emerald-500' : 'bg-rose-500']" class="relative inline-flex rounded-full h-2.5 w-2.5"></span>
              </span>
            </div>
            <h2 class="text-xl font-bold text-slate-100">MariaDB SQL</h2>
            <p class="text-xs text-slate-400 mt-2 leading-relaxed">
              關聯式資料庫。支援自定義 <span class="font-mono text-cyan-400">my_custom.cnf</span> 配置，持久化存於 <span class="font-mono text-cyan-400">./db_data</span>。
            </p>
          </div>
          <div class="mt-6 pt-4 border-t border-slate-800/60 text-xs text-slate-500">
            <div>狀態: <span :class="[(backendData && backendData.database.status === 'connected') ? 'text-emerald-400' : 'text-rose-400']" class="font-semibold">{{ loading ? '檢查中...' : (backendData && backendData.database.status === 'connected') ? '已連線' : '無連線' }}</span></div>
            <div class="mt-1" v-if="backendData && backendData.database.status === 'connected'">庫名: <span class="text-slate-300 font-mono">{{ backendData.database.name }}</span></div>
          </div>
        </div>

        <!-- 5. Cache (Redis 8.8) -->
        <div class="glassmorphism p-6 rounded-2xl flex flex-col justify-between hover:border-rose-500/20 transition-all duration-300" :class="{ 'border-rose-500/30': backendData && backendData.redis.status !== 'connected' }">
          <div>
            <div class="flex justify-between items-start mb-4">
              <span class="text-xs font-bold uppercase tracking-wider text-rose-400 bg-rose-950/40 px-2.5 py-1 rounded-md border border-rose-900/30">Redis 8.8</span>
              <span class="flex h-2.5 w-2.5 relative">
                <span v-if="backendData && backendData.redis.status === 'connected'" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span :class="[loading ? 'bg-amber-500' : (backendData && backendData.redis.status === 'connected') ? 'bg-emerald-500' : 'bg-rose-500']" class="relative inline-flex rounded-full h-2.5 w-2.5"></span>
              </span>
            </div>
            <h2 class="text-xl font-bold text-slate-100">Redis Cache</h2>
            <p class="text-xs text-slate-400 mt-2 leading-relaxed">
              快取與 Session 記憶體伺服器。載入自定義 <span class="font-mono text-rose-400">redis.conf</span>。
            </p>
          </div>
          <div class="mt-6 pt-4 border-t border-slate-800/60 text-xs text-slate-500">
            <div>狀態: <span :class="[(backendData && backendData.redis.status === 'connected') ? 'text-emerald-400' : 'text-rose-400']" class="font-semibold">{{ loading ? '檢查中...' : (backendData && backendData.redis.status === 'connected') ? '已快取' : '無快取' }}</span></div>
            <div class="mt-1">通訊埠: <span class="text-slate-300 font-mono">6379</span></div>
          </div>
        </div>

      </div>

      <!-- 連線異常警告框 -->
      <div v-if="error" class="mt-8 p-4 bg-rose-950/40 border border-rose-900/40 text-rose-300 rounded-xl text-sm flex items-center space-x-3 shadow-md">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-rose-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <span>
          <strong>後端連線異常:</strong> {{ error }}。請確認 Docker 容器已全部正常啟動 (您可以點選上方「手動重新檢測」按鈕再次測試)。
        </span>
      </div>

    </main>

    <!-- 頁尾宣告區 -->
    <footer class="w-full text-center text-xs text-slate-600 mt-8 py-4 border-t border-slate-900/50">
      <p>© 2026 Django 5.2 + Vue 3.5 + Tailwind CSS v4.3 Containerization Stack ( Path: /tech-stack )</p>
      <p class="mt-1">運行於 Linux / Windows Cross-Platform 開發環境 • 定時自動每 10 分鐘連線檢查</p>
    </footer>

  </div>
</template>

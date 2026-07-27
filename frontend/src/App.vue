<!-- ======================================================================= -->
<!-- Vue 3.5 主元件 (App.vue)                                                 -->
<!-- 說明：資訊系統開發環境儀表板 (路由存取點：http://localhost/tech-stack)     -->
<!-- 功能：提供「服務節點健康監控」與「公司資料戰情資訊室」兩大核心 Tab 分頁     -->
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

/**
 * 公司 Profile 資料介面定義 (25個欄位)
 */
interface CompanyProfileData {
  stock_id: string
  tax_id: string | null
  company_name: string
  spokesperson: string | null
  eng_short_name: string | null
  deputy_spokesperson: string | null
  establishment_date: string | null
  phone: string | null
  listing_date: string | null
  fax: string | null
  industry_category: string | null
  website: string | null
  chairman: string | null
  email: string | null
  general_manager: string | null
  stock_transfer_agent: string | null
  capital: number | null
  auditor: string | null
  issued_shares: number | null
  address: string | null
  market_cap_millions: number | null
  market_type: string | null
  insider_holding_ratio: number | null
  group_name: string | null
  main_business: string | null
  created_at: string
  updated_at: string
}

interface CalendarEvent {
  event_type: string
  event_date: string
  description: string | null
}

interface NewsItem {
  news_type: string
  title: string
  url: string
  publisher: string | null
  published_date: string | null
  summary: string | null
}

interface StockFetchResponse {
  success: boolean
  has_data: boolean
  in_schedule?: boolean
  msg?: string
  error?: string
  profile?: CompanyProfileData
  calendar?: CalendarEvent[]
  news?: NewsItem[]
}

// 導覽 Tab 分頁狀態 ('health' | 'dashboard')
const activeTab = ref<'health' | 'dashboard'>('dashboard')
const showTabs = ref(false)

// 根據網址路徑 (window.location.pathname) 分開呈現頁面
if (typeof window !== 'undefined') {
  const path = window.location.pathname
  if (path.includes('/profile')) {
    activeTab.value = 'dashboard'
    showTabs.value = false
  } else if (path.includes('/tech-stack')) {
    activeTab.value = 'health'
    showTabs.value = false
  } else {
    // 若無特殊路徑則同時顯示 Tab (相容預設)
    showTabs.value = true
  }
}

// Tab 1: 健康狀態監控響應式變數
const healthLoading = ref(false)
const healthError = ref<string | null>(null)
const backendHealth = ref<ServiceStatus | null>(null)
const lastCheckedTime = ref<string>('')
const AUTO_REFRESH_INTERVAL_MS = 10 * 60 * 1000
let timerId: ReturnType<typeof setInterval> | null = null

// Tab 2: 戰情室響應式變數
const searchStockId = ref('')
const dashboardLoading = ref(false)
const dashboardError = ref<string | null>(null)
const dashboardSuccessMsg = ref<string | null>(null)
const stockData = ref<StockFetchResponse | null>(null)
let pollIntervalId: ReturnType<typeof setInterval> | null = null

/**
 * 向 Django 後端健康檢查 API (/api/status/) 發送健康檢查請求
 */
const fetchHealthStatus = async () => {
  healthLoading.value = true
  healthError.value = null
  try {
    const res = await fetch('/api/status/')
    if (!res.ok) {
      throw new Error(`HTTP 錯誤! 狀態碼: ${res.status}`)
    }
    backendHealth.value = await res.json()
    const now = new Date()
    lastCheckedTime.value = now.toLocaleTimeString('zh-TW', { hour12: false })
  } catch (err: any) {
    console.error(err)
    healthError.value = err.message || '無法連線至 Django 後端 API'
  } finally {
    healthLoading.value = false
  }
}

/**
 * 股票查詢與即時更新 API (/api/stock/fetch/) 串接 (異步輪詢版本)
 */
const handleStockSearch = async (updateMode: boolean = false) => {
  if (!searchStockId.value.trim()) {
    dashboardError.value = '請輸入台股股票代碼 (例如: 2330)'
    return
  }
  
  if (!/^\d+$/.test(searchStockId.value.trim())) {
    dashboardError.value = '股票代碼必須全部為數字'
    return
  }

  // 清除前次的輪詢
  if (pollIntervalId) {
    clearInterval(pollIntervalId)
    pollIntervalId = null
  }

  dashboardLoading.value = true
  dashboardError.value = null
  dashboardSuccessMsg.value = null

  const stockId = searchStockId.value.trim()

  try {
    const res = await fetch(`/api/stock/fetch/?stock_id=${stockId}&update=${updateMode}`)
    if (!res.ok) {
      const errJson = await res.json().catch(() => ({}))
      throw new Error(errJson.error || `HTTP 錯誤! 狀態碼: ${res.status}`)
    }
    
    const data = await res.json()
    
    if (updateMode && data.task_started) {
      dashboardSuccessMsg.value = `已啟動背景即時抓取更新任務，正在擷取 GNews 與 yfinance 資料...`
      
      // 啟動輪詢，每 3 秒查詢一次本地資料
      let pollCount = 0
      pollIntervalId = setInterval(async () => {
        pollCount++
        try {
          const pollRes = await fetch(`/api/stock/fetch/?stock_id=${stockId}&update=false`)
          if (pollRes.ok) {
            const pollData: StockFetchResponse = await pollRes.json()
            if (pollData.success && pollData.has_data) {
              stockData.value = pollData
              dashboardSuccessMsg.value = `股票 ${stockId} 資料已順利於背景更新完成並落庫！`
              dashboardLoading.value = false
              if (pollIntervalId) {
                clearInterval(pollIntervalId)
                pollIntervalId = null
              }
            }
          }
        } catch (pollErr) {
          console.error("輪詢出錯:", pollErr)
        }

        // 輪詢超過 25 次 (75 秒) 停止，避免無限循環
        if (pollCount >= 25) {
          dashboardError.value = '背景抓取更新超時，請稍後再試。您可以嘗試重新點選本機搜尋。'
          dashboardLoading.value = false
          if (pollIntervalId) {
            clearInterval(pollIntervalId)
            pollIntervalId = null
          }
        }
      }, 3000)
    } else {
      // 純查詢模式
      stockData.value = data
      if (!data.has_data) {
        dashboardError.value = data.msg || '資料庫無此股票資料，請點擊「即時更新並儲存」以重新爬取。'
      }
      dashboardLoading.value = false
    }
  } catch (err: any) {
    console.error(err)
    dashboardError.value = err.message || '連線至後端伺服器失敗'
    dashboardLoading.value = false
  }
}

/**
 * 點擊 More 行事曆，開啟新分頁
 */
const openMoreCalendar = () => {
  if (stockData.value?.profile?.stock_id) {
    window.open(`/stock/calendar/${stockData.value.profile.stock_id}/`, '_blank')
  }
}

/**
 * 點擊 More 新聞，開啟新分頁
 */
const openMoreNews = () => {
  if (stockData.value?.profile?.stock_id) {
    window.open(`/stock/news/${stockData.value.profile.stock_id}/`, '_blank')
  }
}

// 格式化數字 (如股本)
const formatCurrency = (val: number | null) => {
  if (val === null || val === undefined) return '-'
  return new Intl.NumberFormat('zh-TW').format(val)
}

onMounted(() => {
  if (activeTab.value === 'health') {
    // 首次載入頁面時：自動執行健康檢測 1 次
    setTimeout(fetchHealthStatus, 1500)
    // 爾後設定定時器：每 10 分鐘自動重新檢測各服務狀態
    timerId = setInterval(fetchHealthStatus, AUTO_REFRESH_INTERVAL_MS)
  }
})

onUnmounted(() => {
  if (timerId) {
    clearInterval(timerId)
  }
  if (pollIntervalId) {
    clearInterval(pollIntervalId)
  }
})
</script>

<template>
  <div class="min-h-screen bg-[#070b13] text-[#f3f4f6] flex flex-col items-center justify-between p-6 relative overflow-hidden select-none">
    
    <!-- 背景流光漸層光暈 -->
    <div class="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-900/10 rounded-full blur-[120px] pointer-events-none"></div>
    <div class="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-cyan-900/10 rounded-full blur-[120px] pointer-events-none"></div>

    <!-- 主介面容器 -->
    <main class="w-full max-w-6xl z-10 flex-grow flex flex-col my-4">
      
      <!-- 頁頭標題區 -->
      <div class="text-center mb-6">
        <div class="inline-flex items-center space-x-2 bg-slate-900/60 border border-slate-800 px-4 py-1.5 rounded-full text-xs font-semibold tracking-wider text-cyan-400 uppercase mb-3 shadow-sm">
          <span v-if="activeTab === 'dashboard'">📈 Taiwan Stock Profile Room ( /profile )</span>
          <span v-else>🐳 Docker Containerized Stack ( /tech-stack )</span>
        </div>
        <h1 class="text-3xl md:text-4xl font-extrabold tracking-tight bg-gradient-to-r from-white via-cyan-100 to-blue-400 bg-clip-text text-transparent drop-shadow-md">
          <span v-if="activeTab === 'dashboard'">台股公司基本資料戰情室</span>
          <span v-else>系統檢測與健康監控</span>
        </h1>
        <p class="mt-2 text-sm text-slate-400 max-w-2xl mx-auto">
          <span v-if="activeTab === 'dashboard'">
            透過輸入股票代碼搜尋本機庫存，支援手動即時抓取 GNews 與 yfinance 英文資訊並自動英翻中落庫。
          </span>
          <span v-else>
            整合 Django 5.2 LTS, MariaDB 12.3 與 Redis 8.8 容器，動態監控後端與數據庫快取之連線狀態。
          </span>
        </p>

        <!-- 導覽頁籤切換 (Tabs) -->
        <div v-if="showTabs" class="mt-6 inline-flex p-1 bg-slate-900/80 border border-slate-800 rounded-xl">
          <button 
            @click="activeTab = 'dashboard'"
            :class="[activeTab === 'dashboard' ? 'bg-cyan-500 text-[#070b13] font-bold shadow-md' : 'text-slate-400 hover:text-slate-200']"
            class="px-5 py-2 rounded-lg text-xs font-semibold cursor-pointer transition-all duration-300"
          >
            📊 公司資料戰情資訊室
          </button>
          <button 
            @click="activeTab = 'health'"
            :class="[activeTab === 'health' ? 'bg-cyan-500 text-[#070b13] font-bold shadow-md' : 'text-slate-400 hover:text-slate-200']"
            class="px-5 py-2 rounded-lg text-xs font-semibold cursor-pointer transition-all duration-300"
          >
            🐳 服務節點健康監控
          </button>
        </div>
      </div>

      <!-- ======================================================================= -->
      <!-- TAB 1: 公司資料戰情資訊室                                                 -->
      <!-- ======================================================================= -->
      <section v-if="activeTab === 'dashboard'" class="w-full flex-grow flex flex-col space-y-6">
        
        <!-- 股票代碼搜尋控制列 -->
        <div class="glassmorphism p-6 rounded-2xl flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div class="flex-grow flex flex-col md:flex-row md:items-center gap-4">
            <div class="flex-grow relative">
              <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </span>
              <input 
                v-model="searchStockId" 
                @keyup.enter="handleStockSearch(false)"
                type="text" 
                placeholder="請輸入台股股票代碼 (如：2330)" 
                class="w-full pl-10 pr-4 py-2.5 bg-slate-950/80 border border-slate-800 focus:border-cyan-500/80 rounded-xl text-sm font-semibold tracking-wide text-white placeholder-slate-500 outline-none transition-all"
              />
            </div>
            <div class="flex items-center gap-2">
              <button 
                @click="handleStockSearch(false)" 
                :disabled="dashboardLoading"
                class="px-5 py-2.5 bg-slate-900 border border-slate-800 hover:border-slate-700 hover:bg-slate-850 active:bg-slate-900 rounded-xl text-xs font-bold tracking-wider text-cyan-400 cursor-pointer disabled:opacity-50 transition-all"
              >
                {{ dashboardLoading ? '處理中...' : '🔍 本機搜尋' }}
              </button>
              <button 
                @click="handleStockSearch(true)" 
                :disabled="dashboardLoading"
                class="px-5 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-400 hover:to-blue-400 text-darkBg rounded-xl text-xs font-extrabold tracking-wider cursor-pointer disabled:opacity-50 transition-all flex items-center space-x-1 shadow-md shadow-cyan-950/20"
              >
                <svg v-if="dashboardLoading" class="animate-spin h-3.5 w-3.5 text-darkBg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>⚡ 即時更新並儲存</span>
              </button>
            </div>
          </div>
          <div class="text-xs text-slate-500 font-medium md:text-right">
            手動即時更新會將股票加入後台 <span class="text-slate-300 font-mono">Celery Beat</span> 排程清單中。
          </div>
        </div>

        <!-- 狀態提醒列 -->
        <div v-if="dashboardError" class="p-4 bg-rose-950/40 border border-rose-900/40 text-rose-300 rounded-xl text-xs flex items-center space-x-2.5 shadow-md">
          <svg class="h-4 w-4 text-rose-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>{{ dashboardError }}</span>
        </div>
        <div v-if="dashboardSuccessMsg" class="p-4 bg-emerald-950/40 border border-emerald-900/40 text-emerald-300 rounded-xl text-xs flex items-center space-x-2.5 shadow-md">
          <svg class="h-4 w-4 text-emerald-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ dashboardSuccessMsg }}</span>
        </div>

        <!-- 戰情室數據展示面板 -->
        <div v-if="stockData && stockData.has_data && stockData.profile" class="space-y-6">
          
          <!-- 區塊一：股票及公司主資料卡片 -->
          <div class="glassmorphism rounded-2xl p-6 relative overflow-hidden">
            <!-- 裝飾流光 -->
            <div class="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-cyan-500 to-transparent"></div>
            
            <div class="flex flex-col md:flex-row md:items-center md:justify-between border-b border-slate-800/80 pb-4 mb-6">
              <div>
                <h2 class="text-2xl font-black text-slate-100 flex items-center space-x-2">
                  <span>{{ stockData.profile.company_name }}</span>
                  <span class="text-lg text-slate-400 font-mono">({{ stockData.profile.stock_id }})</span>
                </h2>
                <p class="text-xs text-slate-400 mt-1">
                  英文簡稱: {{ stockData.profile.eng_short_name || '-' }} • 統一編號: {{ stockData.profile.tax_id || '-' }}
                </p>
              </div>
              <div class="mt-3 md:mt-0 flex flex-wrap gap-2">
                <span class="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-[10px] font-bold text-cyan-400 uppercase">
                  {{ stockData.profile.market_type }}
                </span>
                <span class="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-[10px] font-bold text-cyan-400">
                  {{ stockData.profile.industry_category }}
                </span>
                <span v-if="stockData.in_schedule" class="px-2.5 py-1 rounded bg-blue-950/60 border border-blue-900/40 text-[10px] font-bold text-blue-300">
                  📅 已排程定時更新
                </span>
              </div>
            </div>

            <!-- 25 項欄位精緻 Grid 展示 -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
              
              <!-- 子分類 1: 營運管理團隊 -->
              <div class="bg-slate-950/40 rounded-xl p-4 border border-slate-900/60">
                <h3 class="text-xs font-black text-cyan-400 mb-3 tracking-wider uppercase flex items-center space-x-1.5">
                  <span class="h-2 w-1 bg-cyan-400 rounded-sm"></span>
                  <span>管理階層成員</span>
                </h3>
                <div class="space-y-2.5 text-xs">
                  <div class="flex justify-between border-b border-slate-900/40 pb-1.5">
                    <span class="text-slate-500">董事長</span>
                    <span class="text-slate-300 font-bold">{{ stockData.profile.chairman || '-' }}</span>
                  </div>
                  <div class="flex justify-between border-b border-slate-900/40 pb-1.5">
                    <span class="text-slate-500">總經理</span>
                    <span class="text-slate-300 font-bold">{{ stockData.profile.general_manager || '-' }}</span>
                  </div>
                  <div class="flex justify-between border-b border-slate-900/40 pb-1.5">
                    <span class="text-slate-500">發言人</span>
                    <span class="text-slate-300">{{ stockData.profile.spokesperson || '-' }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-slate-500">代理發言人</span>
                    <span class="text-slate-300">{{ stockData.profile.deputy_spokesperson || '-' }}</span>
                  </div>
                </div>
              </div>

              <!-- 子分類 2: 資本與市場價值 -->
              <div class="bg-slate-950/40 rounded-xl p-4 border border-slate-900/60">
                <h3 class="text-xs font-black text-cyan-400 mb-3 tracking-wider uppercase flex items-center space-x-1.5">
                  <span class="h-2 w-1 bg-cyan-400 rounded-sm"></span>
                  <span>資本與市值</span>
                </h3>
                <div class="space-y-2.5 text-xs">
                  <div class="flex justify-between border-b border-slate-900/40 pb-1.5">
                    <span class="text-slate-500">市值 (百萬)</span>
                    <span class="text-cyan-300 font-mono font-bold">{{ formatCurrency(stockData.profile.market_cap_millions) }}</span>
                  </div>
                  <div class="flex justify-between border-b border-slate-900/40 pb-1.5">
                    <span class="text-slate-500">實收股本 (元)</span>
                    <span class="text-slate-300 font-mono">{{ formatCurrency(stockData.profile.capital) }}</span>
                  </div>
                  <div class="flex justify-between border-b border-slate-900/40 pb-1.5">
                    <span class="text-slate-500">發行普通股數</span>
                    <span class="text-slate-300 font-mono">{{ formatCurrency(stockData.profile.issued_shares) }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-slate-500">董監持股比例</span>
                    <span class="text-slate-300 font-mono">{{ stockData.profile.insider_holding_ratio !== null ? stockData.profile.insider_holding_ratio + '%' : '-' }}</span>
                  </div>
                </div>
              </div>

              <!-- 子分類 3: 成立與上市時間 -->
              <div class="bg-slate-950/40 rounded-xl p-4 border border-slate-900/60">
                <h3 class="text-xs font-black text-cyan-400 mb-3 tracking-wider uppercase flex items-center space-x-1.5">
                  <span class="h-2 w-1 bg-cyan-400 rounded-sm"></span>
                  <span>成立與掛牌日期</span>
                </h3>
                <div class="space-y-2.5 text-xs">
                  <div class="flex justify-between border-b border-slate-900/40 pb-1.5">
                    <span class="text-slate-500">成立日期</span>
                    <span class="text-slate-300 font-mono">{{ stockData.profile.establishment_date || '-' }}</span>
                  </div>
                  <div class="flex justify-between border-b border-slate-900/40 pb-1.5">
                    <span class="text-slate-500">掛牌日期</span>
                    <span class="text-slate-300 font-mono">{{ stockData.profile.listing_date || '-' }}</span>
                  </div>
                  <div class="flex justify-between border-b border-slate-900/40 pb-1.5">
                    <span class="text-slate-500">所屬集團</span>
                    <span class="text-slate-300">{{ stockData.profile.group_name || '-' }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-slate-500">簽證會計師</span>
                    <span class="text-slate-300">{{ stockData.profile.auditor || '-' }}</span>
                  </div>
                </div>
              </div>

              <!-- 子分類 4: 聯絡與股務代理 -->
              <div class="bg-slate-950/40 rounded-xl p-4 border border-slate-900/60">
                <h3 class="text-xs font-black text-cyan-400 mb-3 tracking-wider uppercase flex items-center space-x-1.5">
                  <span class="h-2 w-1 bg-cyan-400 rounded-sm"></span>
                  <span>聯繫資訊</span>
                </h3>
                <div class="space-y-2.5 text-xs">
                  <div class="flex justify-between border-b border-slate-900/40 pb-1.5">
                    <span class="text-slate-500">總機電話</span>
                    <span class="text-slate-300 font-mono">{{ stockData.profile.phone || '-' }}</span>
                  </div>
                  <div class="flex justify-between border-b border-slate-900/40 pb-1.5">
                    <span class="text-slate-500">電子郵件</span>
                    <span class="text-slate-300 truncate max-w-[150px]">{{ stockData.profile.email || '-' }}</span>
                  </div>
                  <div class="flex justify-between border-b border-slate-900/40 pb-1.5">
                    <span class="text-slate-500">網站</span>
                    <a v-if="stockData.profile.website" :href="stockData.profile.website" target="_blank" class="text-cyan-400 hover:underline truncate max-w-[150px]">
                      {{ stockData.profile.website }}
                    </a>
                    <span v-else class="text-slate-300">-</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-slate-500">傳真號碼</span>
                    <span class="text-slate-300 font-mono">{{ stockData.profile.fax || '-' }}</span>
                  </div>
                </div>
              </div>

            </div>

            <!-- 其他擴充欄位 (地址、股務代理、業務概述) -->
            <div class="mt-6 pt-5 border-t border-slate-800/60 grid grid-cols-1 md:grid-cols-3 gap-6 text-xs">
              <div class="md:col-span-2 space-y-3">
                <div class="flex items-start">
                  <span class="text-slate-500 shrink-0 w-20">公司地址:</span>
                  <span class="text-slate-300">{{ stockData.profile.address || '-' }}</span>
                </div>
                <div class="flex items-start">
                  <span class="text-slate-500 shrink-0 w-20">主要經營業務:</span>
                  <span class="text-slate-300 leading-relaxed font-medium">{{ stockData.profile.main_business || '-' }}</span>
                </div>
              </div>
              <div class="space-y-3">
                <div class="flex justify-between">
                  <span class="text-slate-500">股務代理:</span>
                  <span class="text-slate-300 font-medium">{{ stockData.profile.stock_transfer_agent || '-' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-500">資料更新時間:</span>
                  <span class="text-slate-400 font-mono">{{ stockData.profile.updated_at }}</span>
                </div>
              </div>
            </div>

          </div>

          <!-- 下方左右區塊：行事曆與新聞 -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            <!-- 左側：行事曆 (佔 1/3) -->
            <div class="glassmorphism rounded-2xl p-6 flex flex-col justify-between">
              <div>
                <div class="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                  <h3 class="font-bold text-slate-100 flex items-center space-x-1.5">
                    <span class="h-3 w-1 bg-violet-400 rounded-sm"></span>
                    <span>重大行事曆 (近10筆)</span>
                  </h3>
                  <button 
                    @click="openMoreCalendar" 
                    class="text-[10px] font-black text-violet-400 hover:text-violet-300 border border-violet-800/40 px-2 py-0.5 rounded hover:bg-violet-950/20 cursor-pointer transition"
                  >
                    MORE +
                  </button>
                </div>

                <div v-if="stockData.calendar && stockData.calendar.length" class="space-y-3">
                  <div 
                    v-for="(event, idx) in stockData.calendar" 
                    :key="idx"
                    class="flex items-start justify-between text-xs border-b border-slate-900 pb-2"
                  >
                    <div>
                      <div class="font-bold text-slate-200">{{ event.event_type }}</div>
                      <div class="text-[10px] text-slate-500 mt-0.5">{{ event.description || '除權息/股東會' }}</div>
                    </div>
                    <span class="text-[10px] font-mono text-violet-400 bg-violet-950/30 px-2 py-0.5 rounded border border-violet-900/20">
                      {{ event.event_date }}
                    </span>
                  </div>
                </div>
                <div v-else class="text-center py-10 text-slate-600 text-xs">
                  (無行事曆資料)
                </div>
              </div>
            </div>

            <!-- 右側：相關新聞公告 (佔 2/3) -->
            <div class="glassmorphism rounded-2xl p-6 md:col-span-2 flex flex-col justify-between">
              <div>
                <div class="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                  <h3 class="font-bold text-slate-100 flex items-center space-x-1.5">
                    <span class="h-3 w-1 bg-blue-400 rounded-sm"></span>
                    <span>相關新聞與個股公告 (近10筆)</span>
                  </h3>
                  <button 
                    @click="openMoreNews" 
                    class="text-[10px] font-black text-blue-400 hover:text-blue-300 border border-blue-800/40 px-2 py-0.5 rounded hover:bg-blue-950/20 cursor-pointer transition"
                  >
                    MORE +
                  </button>
                </div>

                <div v-if="stockData.news && stockData.news.length" class="space-y-4">
                  <div 
                    v-for="(news, idx) in stockData.news" 
                    :key="idx" 
                    class="border-b border-slate-900 pb-3 last:border-b-0 text-xs group"
                  >
                    <div class="flex items-center space-x-2 text-[10px] text-slate-500 mb-1">
                      <span class="px-1.5 py-0.5 font-bold rounded" :class="[news.news_type === 'ANNOUNCEMENT' ? 'bg-rose-950/50 text-rose-300' : 'bg-blue-950/50 text-blue-300']">
                        {{ news.news_type === 'ANNOUNCEMENT' ? '公告' : '新聞' }}
                      </span>
                      <span>{{ news.publisher || 'GNews' }}</span>
                      <span>•</span>
                      <span class="font-mono">{{ news.published_date ? news.published_date.slice(0, 16) : '' }}</span>
                    </div>
                    <a :href="news.url" target="_blank" class="font-bold text-slate-200 group-hover:text-cyan-400 hover:underline leading-snug block transition-colors">
                      {{ news.title }}
                    </a>
                  </div>
                </div>
                <div v-else class="text-center py-10 text-slate-600 text-xs">
                  (無新聞公告資料)
                </div>
              </div>
            </div>

          </div>

        </div>

        <div v-else-if="!dashboardLoading" class="glassmorphism rounded-2xl p-16 text-center text-slate-500">
          <svg class="h-12 w-12 mx-auto mb-4 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
          </svg>
          <p class="text-base font-bold text-slate-400">目前尚無股票查詢結果</p>
          <p class="text-xs text-slate-600 mt-1.5 max-w-md mx-auto">
            請於上方搜尋框輸入要查詢的台灣股票代碼 (如：2330)。若資料庫無資料，請點擊「即時更新並儲存」發動爬蟲抓取。
          </p>
        </div>

      </section>

      <!-- ======================================================================= -->
      <!-- TAB 2: 原健康狀態監控儀表板                                               -->
      <!-- ======================================================================= -->
      <section v-if="activeTab === 'health'" class="w-full flex-grow flex flex-col space-y-6">
        
        <!-- 定時檢測說明提示標籤 -->
        <div class="text-center">
          <div class="inline-flex items-center space-x-2 bg-blue-950/40 border border-blue-800/40 px-3 py-1 rounded-full text-xs text-blue-300">
            <span class="relative flex h-2 w-2">
              <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span class="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
            </span>
            <span>首次連線自動檢查 1 次 • 爾後每 10 分鐘自動重新檢測 1 次</span>
            <span v-if="lastCheckedTime" class="text-slate-400 border-l border-slate-700 pl-2 ml-1">上次檢測: {{ lastCheckedTime }}</span>
          </div>
        </div>

        <!-- 快捷操作卡片區 -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          <!-- 卡片 1: Django Admin -->
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

          <!-- 卡片 3: 手動重新檢測 -->
          <button @click="fetchHealthStatus" :disabled="healthLoading" class="glassmorphism p-6 rounded-2xl flex items-center justify-between group hover:border-violet-500/30 transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg hover:shadow-violet-950/20 text-left w-full cursor-pointer">
            <div class="flex items-center space-x-4">
              <div class="p-3 bg-violet-950/40 border border-violet-800/40 text-violet-400 rounded-xl group-hover:bg-violet-500/10 transition-colors" :class="{ 'animate-spin': healthLoading }">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 1121.21 8H17" />
                </svg>
              </div>
              <div>
                <h3 class="font-bold text-slate-200">手動重新檢測</h3>
                <p class="text-xs text-slate-400 mt-0.5">{{ healthLoading ? '檢測中...' : '立即重新測試各容器服務連線' }}</p>
              </div>
            </div>
            <div class="text-slate-500 group-hover:text-violet-400 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" />
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
              <h2 class="text-base font-bold text-slate-100">Apache HTTPD</h2>
              <p class="text-[11px] text-slate-400 mt-2 leading-relaxed">
                反向代理網頁伺服器。監聽 Port 80，分配 /tech-stack、/admin 與 / 路由。
              </p>
            </div>
            <div class="mt-6 pt-4 border-t border-slate-800/60 text-[10px] text-slate-500">
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
              <h2 class="text-base font-bold text-slate-100">Vue.js / Vite</h2>
              <p class="text-[11px] text-slate-400 mt-2 leading-relaxed">
                前端 SPA 技術堆疊，掛載 TypeScript 與 Tailwind CSS 4.3 效能編譯引擎。
              </p>
            </div>
            <div class="mt-6 pt-4 border-t border-slate-800/60 text-[10px] text-slate-500">
              <div>框架版本: <span class="text-slate-300 font-mono">Vue v3.5</span></div>
              <div class="mt-1">樣式引擎: <span class="text-slate-300 font-mono">Tailwind v4.3</span></div>
            </div>
          </div>

          <!-- 3. Backend (Django 5.2) -->
          <div class="glassmorphism p-6 rounded-2xl flex flex-col justify-between hover:border-blue-500/20 transition-all duration-300" :class="{ 'border-rose-500/30': healthError }">
            <div>
              <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold uppercase tracking-wider text-blue-400 bg-blue-950/40 px-2.5 py-1 rounded-md border border-blue-900/30">Django 5.2</span>
                <span class="flex h-2.5 w-2.5 relative">
                  <span v-if="!healthLoading && !healthError" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span :class="[healthLoading ? 'bg-amber-500' : healthError ? 'bg-rose-500' : 'bg-emerald-500']" class="relative inline-flex rounded-full h-2.5 w-2.5"></span>
                </span>
              </div>
              <h2 class="text-base font-bold text-slate-100">Django Backend</h2>
              <p class="text-[11px] text-slate-400 mt-2 leading-relaxed">
                Python Web 後端。負責 REST API、資料庫遷移管理、Celery 排程觸發與 Unfold Admin。
              </p>
            </div>
            <div class="mt-6 pt-4 border-t border-slate-800/60 text-[10px] text-slate-500">
              <div>狀態: <span :class="[healthError ? 'text-rose-400' : 'text-slate-300']" class="font-semibold">{{ healthLoading ? '檢查中...' : healthError ? '連線失敗' : '在線' }}</span></div>
              <div class="mt-1" v-if="backendHealth">版本: <span class="text-slate-300 font-mono">{{ backendHealth.django_version }}</span></div>
            </div>
          </div>

          <!-- 4. Database (MariaDB 12.3) -->
          <div class="glassmorphism p-6 rounded-2xl flex flex-col justify-between hover:border-cyan-500/20 transition-all duration-300" :class="{ 'border-rose-500/30': backendHealth && backendHealth.database.status !== 'connected' }">
            <div>
              <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold uppercase tracking-wider text-cyan-400 bg-cyan-950/40 px-2.5 py-1 rounded-md border border-cyan-900/30">MariaDB 12.3</span>
                <span class="flex h-2.5 w-2.5 relative">
                  <span v-if="backendHealth && backendHealth.database.status === 'connected'" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span :class="[healthLoading ? 'bg-amber-500' : (backendHealth && backendHealth.database.status === 'connected') ? 'bg-emerald-500' : 'bg-rose-500']" class="relative inline-flex rounded-full h-2.5 w-2.5"></span>
                </span>
              </div>
              <h2 class="text-base font-bold text-slate-100">MariaDB SQL</h2>
              <p class="text-[11px] text-slate-400 mt-2 leading-relaxed">
                SQL 資料庫，提供 user_stock 與 user_employee 權限隔離與實體 `./db_data` 持久化。
              </p>
            </div>
            <div class="mt-6 pt-4 border-t border-slate-800/60 text-[10px] text-slate-500">
              <div>狀態: <span :class="[(backendHealth && backendHealth.database.status === 'connected') ? 'text-emerald-400' : 'text-rose-400']" class="font-semibold">{{ healthLoading ? '檢查中...' : (backendHealth && backendHealth.database.status === 'connected') ? '已連線' : '無連線' }}</span></div>
              <div class="mt-1" v-if="backendHealth && backendHealth.database.status === 'connected'">庫名: <span class="text-slate-300 font-mono">{{ backendHealth.database.name }}</span></div>
            </div>
          </div>

          <!-- 5. Cache (Redis 8.8) -->
          <div class="glassmorphism p-6 rounded-2xl flex flex-col justify-between hover:border-rose-500/20 transition-all duration-300" :class="{ 'border-rose-500/30': backendHealth && backendHealth.redis.status !== 'connected' }">
            <div>
              <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold uppercase tracking-wider text-rose-400 bg-rose-950/40 px-2.5 py-1 rounded-md border border-rose-900/30">Redis 8.8</span>
                <span class="flex h-2.5 w-2.5 relative">
                  <span v-if="backendHealth && backendHealth.redis.status === 'connected'" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span :class="[healthLoading ? 'bg-amber-500' : (backendHealth && backendHealth.redis.status === 'connected') ? 'bg-emerald-500' : 'bg-rose-500']" class="relative inline-flex rounded-full h-2.5 w-2.5"></span>
                </span>
              </div>
              <h2 class="text-base font-bold text-slate-100">Redis Cache</h2>
              <p class="text-[11px] text-slate-400 mt-2 leading-relaxed">
                快取與 Session 記憶體伺服器。執行高併發快取儲存，掛載實體 `./redis_data`。
              </p>
            </div>
            <div class="mt-6 pt-4 border-t border-slate-800/60 text-[10px] text-slate-500">
              <div>狀態: <span :class="[(backendHealth && backendHealth.redis.status === 'connected') ? 'text-emerald-400' : 'text-rose-400']" class="font-semibold">{{ healthLoading ? '檢查中...' : (backendHealth && backendHealth.redis.status === 'connected') ? '已快取' : '無快取' }}</span></div>
              <div class="mt-1">通訊埠: <span class="text-slate-300 font-mono">6379</span></div>
            </div>
          </div>

        </div>

        <!-- 連線異常警告框 -->
        <div v-if="healthError" class="mt-8 p-4 bg-rose-950/40 border border-rose-900/40 text-rose-300 rounded-xl text-sm flex items-center space-x-3 shadow-md">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-rose-400 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <span>
            <strong>後端連線異常:</strong> {{ healthError }}。請確認 Docker 容器已全部正常啟動 (您可以點選上方「手動重新檢測」按鈕再次測試)。
          </span>
        </div>

      </section>

    </main>

    <!-- 頁尾宣告區 -->
    <footer class="w-full text-center text-xs text-slate-600 mt-8 py-4 border-t border-slate-900/50">
      <p>© 2026 Django 5.2 + Vue 3.5 + Tailwind CSS v4.3 Containerization Stack ( Path: /tech-stack )</p>
      <p class="mt-1 font-medium">
        運行於 Linux / Windows Cross-Platform 開發環境 • 
        <span v-if="activeTab === 'health'">定時自動每 10 分鐘連線檢查</span>
        <span v-else>支援手動重新連線檢查</span>
      </p>
    </footer>

  </div>
</template>

<style>
/* 可以在這裡加入額外覆寫 */
</style>

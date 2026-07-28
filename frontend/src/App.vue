<!-- ======================================================================= -->
<!-- Vue 3.5 主元件 (App.vue)                                                 -->
<!-- 說明：資訊系統開發環境與台股戰情室儀表板                                   -->
<!-- ======================================================================= -->
<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'

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

interface TechnicalAnalysisData {
  trade_date: string
  volume: number | null
  open_price: number | null
  high_price: number | null
  low_price: number | null
  close_price: number | null
  k_value: number | null
  d_value: number | null
  j_value: number | null
  macd: number | null
  macd_signal: number | null
  bias: number | null
  williams_r: number | null
  bbi: number | null
  cdp: number | null
  ah: number | null
  nh: number | null
  nl: number | null
  al: number | null
  pdi: number | null
  mdi: number | null
  adx: number | null
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
  technical_analysis?: TechnicalAnalysisData[]
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

// Tab 2: 戰情室與技術分析響應式變數
const searchStockId = ref('')
const dashboardLoading = ref(false)
const dashboardError = ref<string | null>(null)
const dashboardSuccessMsg = ref<string | null>(null)
const stockData = ref<StockFetchResponse | null>(null)
const activeSubTab = ref<'profile' | 'ta'>('profile') // 'profile' 為基本面，'ta' 為技術分析
const selectedIndicator = ref<'kd' | 'macd' | 'dmi' | 'bias' | 'williams'>('kd') // 當前技術指標子圖
const taChartRef = ref<HTMLDivElement | null>(null)
let myChart: echarts.ECharts | null = null
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
  
  // 清理先前的狀態與定時輪詢
  dashboardError.value = null
  dashboardSuccessMsg.value = null
  if (pollIntervalId) {
    clearInterval(pollIntervalId)
    pollIntervalId = null
  }

  dashboardLoading.value = true

  try {
    const res = await fetch(`/api/stock/fetch/?stock_id=${searchStockId.value.trim()}&update=${updateMode}`)
    if (!res.ok) {
      const errData = await res.json()
      throw new Error(errData.error || `HTTP 錯誤: ${res.status}`)
    }

    const data: StockFetchResponse = await res.json()

    if (updateMode && data.task_started) {
      // 進入背景非同步輪詢模式，每 3 秒檢查一次資料是否完成寫入
      dashboardSuccessMsg.value = '已啟動背景資料擷取與翻譯排程，大約需要 3 - 5 秒，系統正自動為您同步數據...'
      
      let attempts = 0
      pollIntervalId = setInterval(async () => {
        attempts++
        if (attempts > 30) {
          // 超過 90 秒停止輪詢，避免連線無限拉長
          clearInterval(pollIntervalId!)
          pollIntervalId = null
          dashboardLoading.value = false
          dashboardError.value = '更新逾時，外部伺服器連線遲緩，請稍後再試。'
          return
        }

        try {
          const pollRes = await fetch(`/api/stock/fetch/?stock_id=${searchStockId.value.trim()}&update=false`)
          if (pollRes.ok) {
            const pollData: StockFetchResponse = await pollRes.json()
            if (pollData.success && pollData.has_data && pollData.profile) {
              // 成功撈到最新資料，停止輪詢並渲染
              clearInterval(pollIntervalId!)
              pollIntervalId = null
              stockData.value = pollData
              dashboardSuccessMsg.value = '🎉 資料庫落庫與技術分析計算完成！已成功渲染最新數據！'
              dashboardLoading.value = false
            }
          }
        } catch (pollErr) {
          console.error('輪詢出錯: ', pollErr)
        }
      }, 3000)

    } else {
      // 純查詢模式，直接渲染資料
      stockData.value = data
      if (!data.has_data) {
        dashboardError.value = '本機資料庫無此股票資料，請點擊「即時更新並儲存」啟動爬蟲'
      }
      dashboardLoading.value = false
    }
  } catch (err: any) {
    console.error(err)
    dashboardError.value = err.message || '連線至後端股票 API 失敗'
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

/**
 * 初始化 Apache ECharts 技術分析綜合圖表
 */
const initTaChart = () => {
  if (!taChartRef.value || !stockData.value || !stockData.value.technical_analysis || stockData.value.technical_analysis.length === 0) {
    return
  }

  // 銷毀舊有實例防止 Memory Leak
  if (myChart) {
    myChart.dispose()
  }

  myChart = echarts.init(taChartRef.value, 'dark')

  const taList = stockData.value.technical_analysis
  const dates = taList.map(item => item.trade_date)
  const volumes = taList.map(item => item.volume)

  // K線 [open, close, lowest, highest]
  const candlestickData = taList.map(item => [
    item.open_price,
    item.close_price,
    item.low_price,
    item.high_price
  ])

  // BBI / CDP 折線
  const bbiData = taList.map(item => item.bbi)
  const cdpData = taList.map(item => item.cdp)

  // 1. KD
  const kData = taList.map(item => item.k_value)
  const dData = taList.map(item => item.d_value)
  const jData = taList.map(item => item.j_value)

  // 2. MACD
  const difData = taList.map(item => item.macd)
  const deaData = taList.map(item => item.macd_signal)
  const macdHistData = taList.map(item => {
    if (item.macd !== null && item.macd_signal !== null) {
      return (item.macd - item.macd_signal) * 2
    }
    return null
  })

  // 3. DMI
  const pdiData = taList.map(item => item.pdi)
  const mdiData = taList.map(item => item.mdi)
  const adxData = taList.map(item => item.adx)

  // 4. BIAS (6日)
  const biasData = taList.map(item => item.bias)

  // 5. Williams %R (14日)
  const williamsData = taList.map(item => item.williams_r)

  // 依據前端選擇的指標，定義子圖3的 Series 與 Legend
  let indicatorSeries: any[] = []
  let indicatorLegend: string[] = []

  if (selectedIndicator.value === 'kd') {
    indicatorLegend = ['K值(9日)', 'D值(9日)', 'J值(9日)']
    indicatorSeries = [
      { name: 'K值(9日)', type: 'line', data: kData, xAxisIndex: 2, yAxisIndex: 2, showSymbol: false, lineStyle: { width: 1.5, color: '#f59e0b' } },
      { name: 'D值(9日)', type: 'line', data: dData, xAxisIndex: 2, yAxisIndex: 2, showSymbol: false, lineStyle: { width: 1.5, color: '#3b82f6' } },
      { name: 'J值(9日)', type: 'line', data: jData, xAxisIndex: 2, yAxisIndex: 2, showSymbol: false, lineStyle: { width: 1.5, color: '#a855f7' } }
    ]
  } else if (selectedIndicator.value === 'macd') {
    indicatorLegend = ['DIF (MACD)', 'DEA (Signal)', 'MACD Bar']
    indicatorSeries = [
      { name: 'DIF (MACD)', type: 'line', data: difData, xAxisIndex: 2, yAxisIndex: 2, showSymbol: false, lineStyle: { width: 1.5, color: '#f59e0b' } },
      { name: 'DEA (Signal)', type: 'line', data: deaData, xAxisIndex: 2, yAxisIndex: 2, showSymbol: false, lineStyle: { width: 1.5, color: '#3b82f6' } },
      {
        name: 'MACD Bar',
        type: 'bar',
        data: macdHistData,
        xAxisIndex: 2,
        yAxisIndex: 2,
        itemStyle: {
          color: (params: any) => params.data >= 0 ? '#ef4444' : '#10b981'
        }
      }
    ]
  } else if (selectedIndicator.value === 'dmi') {
    indicatorLegend = ['+DI', '-DI', 'ADX']
    indicatorSeries = [
      { name: '+DI', type: 'line', data: pdiData, xAxisIndex: 2, yAxisIndex: 2, showSymbol: false, lineStyle: { width: 1.5, color: '#ef4444' } },
      { name: '-DI', type: 'line', data: mdiData, xAxisIndex: 2, yAxisIndex: 2, showSymbol: false, lineStyle: { width: 1.5, color: '#10b981' } },
      { name: 'ADX', type: 'line', data: adxData, xAxisIndex: 2, yAxisIndex: 2, showSymbol: false, lineStyle: { width: 1.5, color: '#f59e0b' } }
    ]
  } else if (selectedIndicator.value === 'bias') {
    indicatorLegend = ['BIAS (6日)']
    indicatorSeries = [
      { name: 'BIAS (6日)', type: 'line', data: biasData, xAxisIndex: 2, yAxisIndex: 2, showSymbol: false, lineStyle: { width: 1.5, color: '#ec4899' } }
    ]
  } else if (selectedIndicator.value === 'williams') {
    indicatorLegend = ['Williams %R (14日)']
    indicatorSeries = [
      { name: 'Williams %R (14日)', type: 'line', data: williamsData, xAxisIndex: 2, yAxisIndex: 2, showSymbol: false, lineStyle: { width: 1.5, color: '#14b8a6' } }
    ]
  }

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['日K線', 'BBI', 'CDP', '成交量', ...indicatorLegend],
      textStyle: { color: '#94a3b8' }
    },
    axisPointer: {
      link: [{ xAxisIndex: 'all' }]
    },
    grid: [
      { left: '8%', right: '4%', height: '45%' }, // 主K線
      { left: '8%', right: '4%', top: '60%', height: '12%' }, // 成交量
      { left: '8%', right: '4%', top: '78%', height: '15%' }  // 指標
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        boundaryGap: false,
        axisLine: { lineStyle: { color: '#334155' } },
        axisLabel: { color: '#94a3b8' }
      },
      {
        type: 'category',
        gridIndex: 1,
        data: dates,
        boundaryGap: false,
        axisLine: { lineStyle: { color: '#334155' } },
        axisLabel: { show: false }
      },
      {
        type: 'category',
        gridIndex: 2,
        data: dates,
        boundaryGap: false,
        axisLine: { lineStyle: { color: '#334155' } },
        axisLabel: { color: '#94a3b8' }
      }
    ],
    yAxis: [
      {
        scale: true,
        axisLine: { lineStyle: { color: '#334155' } },
        axisLabel: { color: '#94a3b8' },
        splitLine: { lineStyle: { color: '#1e293b' } }
      },
      {
        scale: true,
        gridIndex: 1,
        axisLine: { show: false },
        axisLabel: { show: false },
        splitLine: { show: false }
      },
      {
        scale: true,
        gridIndex: 2,
        axisLine: { lineStyle: { color: '#334155' } },
        axisLabel: { color: '#94a3b8' },
        splitLine: { lineStyle: { color: '#1e293b' } }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1, 2],
        start: 70,
        end: 100
      },
      {
        show: true,
        type: 'slider',
        xAxisIndex: [0, 1, 2],
        top: '94%',
        start: 70,
        end: 100,
        textStyle: { color: '#94a3b8' }
      }
    ],
    series: [
      {
        name: '日K線',
        type: 'candlestick',
        data: candlestickData,
        itemStyle: {
          color: '#ef4444',
          color0: '#10b981',
          borderColor: '#ef4444',
          borderColor0: '#10b981'
        }
      },
      {
        name: 'BBI',
        type: 'line',
        data: bbiData,
        showSymbol: false,
        lineStyle: { width: 1.5, color: '#f43f5e' }
      },
      {
        name: 'CDP',
        type: 'line',
        data: cdpData,
        showSymbol: false,
        lineStyle: { width: 1.5, type: 'dashed', color: '#06b6d4' }
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumes,
        itemStyle: {
          color: (params: any) => {
            const idx = params.dataIndex
            const row = candlestickData[idx]
            if (row && row[1] >= row[0]) {
              return '#ef4444'
            }
            return '#10b981'
          }
        }
      },
      ...indicatorSeries
    ]
  }

  myChart.setOption(option)
}

// 監聽子頁籤切換、指標切換以及股票資料更新以重繪 ECharts
watch([activeSubTab, selectedIndicator, stockData], async () => {
  if (activeSubTab.value === 'ta') {
    await nextTick()
    initTaChart()
  }
})

// 監聽視窗大小調整以自適應 ECharts 佈局
const handleResize = () => {
  if (myChart) {
    myChart.resize()
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  if (activeTab.value === 'health') {
    // 首次載入頁面時：自動執行健康檢測 1 次
    setTimeout(fetchHealthStatus, 1500)
    // 爾後設定定時器：每 10 分鐘自動重新檢測各服務狀態
    timerId = setInterval(fetchHealthStatus, AUTO_REFRESH_INTERVAL_MS)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (timerId) {
    clearInterval(timerId)
  }
  if (pollIntervalId) {
    clearInterval(pollIntervalId)
  }
  if (myChart) {
    myChart.dispose()
  }
})
</script>

<template>
  <div class="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans antialiased selection:bg-cyan-500/30 selection:text-cyan-200">
    
    <!-- 頂部霓虹流光背景 -->
    <div class="fixed top-0 left-0 w-full h-[350px] bg-gradient-to-b from-cyan-950/20 via-slate-950/0 to-transparent pointer-events-none z-0"></div>
    <div class="fixed top-[-100px] left-[20%] w-[600px] h-[300px] bg-cyan-500/10 rounded-full blur-[120px] pointer-events-none z-0"></div>
    
    <!-- 頂部導航列 -->
    <header class="w-full border-b border-slate-900 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        
        <!-- LOGO 區 -->
        <div class="flex items-center space-x-3 select-none">
          <div class="h-9 w-9 rounded-xl bg-gradient-to-br from-cyan-400 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <svg class="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <div>
            <span class="text-base font-black tracking-wider bg-gradient-to-r from-slate-100 to-slate-300 bg-clip-text text-transparent">FINANCIAL</span>
            <span class="text-xs font-bold text-cyan-400 block tracking-widest leading-none mt-0.5">CONTAINER STACK</span>
          </div>
        </div>

        <!-- 導航分頁切換按鈕 (根據 showTabs 狀態動態隱藏) -->
        <nav v-if="showTabs" class="flex space-x-1 p-1 bg-slate-900/60 rounded-xl border border-slate-800/40">
          <button 
            @click="activeTab = 'dashboard'" 
            :class="[activeTab === 'dashboard' ? 'bg-cyan-500/25 text-cyan-300 border-cyan-500/30' : 'text-slate-400 hover:text-slate-200 border-transparent']"
            class="px-4 py-1.5 text-xs font-bold rounded-lg transition-all duration-300 border"
          >
            台股戰情室
          </button>
          <button 
            @click="activeTab = 'health'" 
            :class="[activeTab === 'health' ? 'bg-cyan-500/25 text-cyan-300 border-cyan-500/30' : 'text-slate-400 hover:text-slate-200 border-transparent']"
            class="px-4 py-1.5 text-xs font-bold rounded-lg transition-all duration-300 border"
          >
            服務節點監控
          </button>
        </nav>

        <!-- 管理後台快速跳轉 -->
        <a 
          href="/admin/" 
          target="_blank" 
          class="px-3.5 py-1.5 text-xs font-bold text-slate-300 hover:text-slate-100 bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl transition-all duration-300 flex items-center space-x-1.5 shadow-sm"
        >
          <span>管理後台</span>
          <svg class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
          </svg>
        </a>

      </div>
    </header>

    <!-- 主要內容區 -->
    <main class="flex-grow max-w-7xl w-full mx-auto px-6 py-8 relative z-10">

      <!-- ======================================================================= -->
      <!-- SECTION 1: 公司基本資料戰情室 (Dashboard)                                -->
      <!-- ======================================================================= -->
      <section v-if="activeTab === 'dashboard'" class="space-y-6">
        
        <!-- 頂部搜尋與功能控制卡片 -->
        <div class="glassmorphism rounded-2xl p-6 shadow-2xl border border-slate-900/50">
          <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            
            <!-- 搜尋輸入框與控制 -->
            <div class="flex items-center space-x-2.5 max-w-lg w-full">
              <div class="relative flex-grow">
                <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                  <svg class="h-4 w-4 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <input 
                  type="text" 
                  v-model="searchStockId" 
                  @keyup.enter="handleStockSearch(false)"
                  placeholder="請輸入台灣股市代碼 (例如: 2330, 2454)" 
                  class="w-full bg-slate-950/80 border border-slate-800 hover:border-slate-700 focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 rounded-xl py-2.5 pl-10 pr-4 text-sm font-medium text-slate-100 placeholder-slate-500 transition-all outline-none"
                />
              </div>
              <button 
                @click="handleStockSearch(false)" 
                :disabled="dashboardLoading"
                class="px-5 py-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-200 text-sm font-bold rounded-xl transition-all duration-300 shrink-0 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                搜尋
              </button>
              <button 
                @click="handleStockSearch(true)" 
                :disabled="dashboardLoading"
                class="px-5 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-sm font-bold rounded-xl transition-all duration-300 shadow-md shadow-cyan-500/20 shrink-0 cursor-pointer flex items-center space-x-1.5 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg v-if="dashboardLoading" class="animate-spin h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>⚡ 即時更新並儲存</span>
              </button>
            </div>
            
            <div class="text-xs text-slate-500 font-medium md:text-right">
              本機資料搜尋為實時回應；即時更新抓取將股票自動加入後台 <span class="text-slate-300 font-mono">Celery Beat</span> 定時排程清單。
            </div>
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

        <!-- 戰情室數據展示主分頁 (當前有股票資料時顯示) -->
        <div v-if="stockData && stockData.has_data && stockData.profile" class="space-y-6">
          
          <!-- 子頁籤切換 Tabs (📋 公司基本資料與新聞 VS 📈 技術分析圖表) -->
          <div class="flex gap-4 border-b border-slate-900 pb-2">
            <button 
              @click="activeSubTab = 'profile'" 
              :class="[
                'px-4 py-2 text-sm font-bold rounded-lg transition-all duration-300 flex items-center gap-2 cursor-pointer',
                activeSubTab === 'profile' 
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-[0_0_15px_rgba(6,182,212,0.15)]' 
                  : 'text-slate-400 hover:text-slate-200 border border-transparent'
              ]"
            >
              📋 公司基本資料與新聞
            </button>
            <button 
              @click="activeSubTab = 'ta'" 
              :class="[
                'px-4 py-2 text-sm font-bold rounded-lg transition-all duration-300 flex items-center gap-2 cursor-pointer',
                activeSubTab === 'ta' 
                  ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/40 shadow-[0_0_15px_rgba(6,182,212,0.15)]' 
                  : 'text-slate-400 hover:text-slate-200 border border-transparent'
              ]"
            >
              📈 技術分析圖表
            </button>
          </div>

          <!-- 子頁籤 A：公司基本資料與新聞 -->
          <div v-if="activeSubTab === 'profile'" class="space-y-6">
            
            <!-- 股票及公司主資料卡片 -->
            <div class="glassmorphism rounded-2xl p-6 relative overflow-hidden">
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
                
                <div class="flex items-center space-x-2 mt-4 md:mt-0">
                  <span class="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-[10px] font-bold text-cyan-400 tracking-wider">
                    {{ stockData.profile.market_type }}
                  </span>
                  <span class="px-2.5 py-1 rounded bg-slate-900 border border-slate-800 text-[10px] font-bold text-slate-300 tracking-wider">
                    {{ stockData.profile.industry_category }}
                  </span>
                  <span v-if="stockData.in_schedule" class="px-2.5 py-1 rounded bg-blue-950/60 border border-blue-900/40 text-[10px] font-bold text-blue-300">
                    已加入定時排程
                  </span>
                </div>
              </div>

              <!-- 4 大維度指標 Grid (基本經營、市值股本、時間節點、聯絡窗口) -->
              <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
                
                <!-- 欄位維度 1: 經營治理 -->
                <div class="bg-slate-950/40 rounded-xl p-4 border border-slate-900">
                  <h3 class="text-xs font-bold text-slate-400 border-b border-slate-800/60 pb-2 mb-3">👔 經營與治理團隊</h3>
                  <div class="space-y-2.5 text-xs">
                    <div class="flex justify-between"><span class="text-slate-500">董事長</span><span class="text-slate-300 font-bold">{{ stockData.profile.chairman || '-' }}</span></div>
                    <div class="flex justify-between"><span class="text-slate-500">總經理</span><span class="text-slate-300 font-bold">{{ stockData.profile.general_manager || '-' }}</span></div>
                    <div class="flex justify-between"><span class="text-slate-500">發言人</span><span class="text-slate-300">{{ stockData.profile.spokesperson || '-' }}</span></div>
                    <div class="flex justify-between"><span class="text-slate-500">代理發言人</span><span class="text-slate-300">{{ stockData.profile.deputy_spokesperson || '-' }}</span></div>
                  </div>
                </div>

                <!-- 欄位維度 2: 市值股本 -->
                <div class="bg-slate-950/40 rounded-xl p-4 border border-slate-900">
                  <h3 class="text-xs font-bold text-slate-400 border-b border-slate-800/60 pb-2 mb-3">💰 股本與市值規模</h3>
                  <div class="space-y-2.5 text-xs">
                    <div class="flex justify-between"><span class="text-slate-500">市值 (百萬)</span><span class="text-cyan-300 font-mono font-bold">{{ formatCurrency(stockData.profile.market_cap_millions) }}</span></div>
                    <div class="flex justify-between"><span class="text-slate-500">股本 (元)</span><span class="text-slate-300 font-mono">{{ formatCurrency(stockData.profile.capital) }}</span></div>
                    <div class="flex justify-between"><span class="text-slate-500">已發行普通股數</span><span class="text-slate-300 font-mono">{{ formatCurrency(stockData.profile.issued_shares) }}</span></div>
                    <div class="flex justify-between"><span class="text-slate-500">董監持股比例</span><span class="text-slate-300 font-mono">{{ stockData.profile.insider_holding_ratio !== null ? stockData.profile.insider_holding_ratio + '%' : '-' }}</span></div>
                  </div>
                </div>

                <!-- 欄位維度 3: 歷史時間 -->
                <div class="bg-slate-950/40 rounded-xl p-4 border border-slate-900">
                  <h3 class="text-xs font-bold text-slate-400 border-b border-slate-800/60 pb-2 mb-3">📅 成立與掛牌時間</h3>
                  <div class="space-y-2.5 text-xs">
                    <div class="flex justify-between"><span class="text-slate-500">成立日期</span><span class="text-slate-300 font-mono">{{ stockData.profile.establishment_date || '-' }}</span></div>
                    <div class="flex justify-between"><span class="text-slate-500">掛牌日期</span><span class="text-slate-300 font-mono">{{ stockData.profile.listing_date || '-' }}</span></div>
                    <div class="flex justify-between"><span class="text-slate-500">所屬集團</span><span class="text-slate-300">{{ stockData.profile.group_name || '-' }}</span></div>
                    <div class="flex justify-between"><span class="text-slate-500">簽證會計師</span><span class="text-slate-300">{{ stockData.profile.auditor || '-' }}</span></div>
                  </div>
                </div>

                <!-- 欄位維度 4: 聯絡資訊 -->
                <div class="bg-slate-950/40 rounded-xl p-4 border border-slate-900">
                  <h3 class="text-xs font-bold text-slate-400 border-b border-slate-800/60 pb-2 mb-3">📞 聯絡窗口與網站</h3>
                  <div class="space-y-2.5 text-xs">
                    <div class="flex justify-between"><span class="text-slate-500">總機電話</span><span class="text-slate-300 font-mono">{{ stockData.profile.phone || '-' }}</span></div>
                    <div class="flex justify-between"><span class="text-slate-500">電子郵件</span><span class="text-slate-300 truncate max-w-[150px]">{{ stockData.profile.email || '-' }}</span></div>
                    <div class="flex justify-between">
                      <span class="text-slate-500">公司網站</span>
                      <a v-if="stockData.profile.website" :href="stockData.profile.website" target="_blank" class="text-cyan-400 hover:underline truncate max-w-[150px]">
                        {{ stockData.profile.website }}
                      </a>
                      <span v-else class="text-slate-300">-</span>
                    </div>
                    <div class="flex justify-between"><span class="text-slate-500">傳真號碼</span><span class="text-slate-300 font-mono">{{ stockData.profile.fax || '-' }}</span></div>
                  </div>
                </div>

              </div>

              <!-- 地址、業務經營及落庫更新時間 -->
              <div class="mt-6 pt-6 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-12 gap-4 text-xs">
                <div class="md:col-span-12 flex flex-col md:flex-row md:items-center"><span class="text-slate-500 font-bold shrink-0 w-24">公司地址：</span><span class="text-slate-300">{{ stockData.profile.address || '-' }}</span></div>
                <div class="md:col-span-12 flex flex-col md:flex-row md:items-start"><span class="text-slate-500 font-bold shrink-0 w-24 mt-1">主要經營業務：</span><span class="text-slate-300 leading-relaxed font-medium">{{ stockData.profile.main_business || '-' }}</span></div>
                <div class="md:col-span-12 flex flex-col md:flex-row md:items-center"><span class="text-slate-500 font-bold shrink-0 w-24">股務代理機構：</span><span class="text-slate-300 font-medium">{{ stockData.profile.stock_transfer_agent || '-' }}</span></div>
                
                <div class="md:col-span-12 text-right text-[10px] text-slate-500 mt-2">
                  <span>資料更新時間: {{ stockData.profile.updated_at }} (Aisa/Taipei Time)</span>
                </div>
              </div>

            </div>

            <!-- 下方行事曆與相關新聞雙欄 -->
            <div class="grid grid-cols-1 md:grid-cols-12 gap-6">
              
              <!-- 股東常會與股利發放行事曆 (佔 5 欄) -->
              <div class="md:col-span-5 glassmorphism rounded-2xl p-6 border border-slate-900/50 flex flex-col">
                <div class="flex items-center justify-between border-b border-slate-800/80 pb-4 mb-4">
                  <div class="flex items-center space-x-2">
                    <div class="w-1 h-4 bg-cyan-500 rounded"></div>
                    <h3 class="text-sm font-bold text-slate-100">📅 股東會與股利發放行事曆</h3>
                  </div>
                  <button @click="openMoreCalendar" class="text-xs font-bold text-cyan-400 hover:text-cyan-300 flex items-center space-x-0.5 cursor-pointer">
                    <span>MORE</span>
                    <span>+</span>
                  </button>
                </div>
                
                <div v-if="stockData.calendar && stockData.calendar.length" class="space-y-3 flex-grow">
                  <div 
                    v-for="(event, idx) in stockData.calendar" 
                    :key="idx"
                    class="p-3 bg-slate-950/40 border border-slate-900 rounded-xl flex items-center justify-between text-xs"
                  >
                    <div>
                      <span class="font-bold text-slate-200">{{ event.event_type }}</span>
                      <p class="text-[10px] text-slate-500 mt-1">{{ event.description || '無詳細描述' }}</p>
                    </div>
                    <span class="font-mono text-cyan-400 font-bold bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-900/40">
                      {{ event.event_date }}
                    </span>
                  </div>
                </div>
                <div v-else class="text-center py-12 text-slate-500 text-xs flex-grow flex items-center justify-center">
                  目前無重大行事曆資料。
                </div>
              </div>

              <!-- 近 10 筆相關新聞與個股公告 (佔 7 欄) -->
              <div class="md:col-span-7 glassmorphism rounded-2xl p-6 border border-slate-900/50 flex flex-col">
                <div class="flex items-center justify-between border-b border-slate-800/80 pb-4 mb-4">
                  <div class="flex items-center space-x-2">
                    <div class="w-1 h-4 bg-cyan-500 rounded"></div>
                    <h3 class="text-sm font-bold text-slate-100">📰 相關新聞與個股公告</h3>
                  </div>
                  <button @click="openMoreNews" class="text-xs font-bold text-cyan-400 hover:text-cyan-300 flex items-center space-x-0.5 cursor-pointer">
                    <span>MORE</span>
                    <span>+</span>
                  </button>
                </div>

                <div v-if="stockData.news && stockData.news.length" class="space-y-4 flex-grow">
                  <div 
                    v-for="(news, idx) in stockData.news" 
                    :key="idx"
                    class="p-3.5 bg-slate-950/40 border border-slate-900 hover:border-slate-800 rounded-xl transition text-xs relative overflow-hidden"
                  >
                    <div class="flex items-center justify-between mb-2">
                      <span :class="[news.news_type === 'NEWS' ? 'bg-indigo-950/50 text-indigo-400 border border-indigo-900/40' : 'bg-amber-950/50 text-amber-400 border border-amber-900/40']" class="px-2 py-0.5 rounded text-[10px] font-bold">
                        {{ news.news_type }}
                      </span>
                      <span class="text-[10px] text-slate-500 font-mono">{{ news.published_date || '-' }}</span>
                    </div>
                    <a :href="news.url" target="_blank" class="font-bold text-slate-200 hover:text-cyan-400 hover:underline leading-relaxed block">
                      {{ news.title }}
                    </a>
                    <p class="text-[10px] text-slate-500 mt-2 line-clamp-2 leading-relaxed">
                      {{ news.summary || '無摘要說明。' }}
                    </p>
                    <div class="text-[10px] text-cyan-500 mt-2 font-semibold">來源: {{ news.publisher || '未知' }}</div>
                  </div>
                </div>
                <div v-else class="text-center py-12 text-slate-500 text-xs flex-grow flex items-center justify-center">
                  目前無相關新聞與公告。
                </div>
              </div>

            </div>

          </div>

          <!-- 子頁籤 B：技術分析圖表 -->
          <div v-else-if="activeSubTab === 'ta'" class="space-y-6">
            
            <div class="glassmorphism rounded-2xl p-6 relative overflow-hidden">
              <div class="absolute top-0 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-cyan-500 to-transparent"></div>
              
              <!-- 圖表頂部指標切換選單 -->
              <div class="flex flex-col md:flex-row md:items-center md:justify-between border-b border-slate-800/80 pb-4 mb-6 gap-4">
                <div>
                  <h3 class="text-lg font-black text-slate-100 flex items-center space-x-2">
                    <span>{{ stockData.profile.company_name }} 個股技術分析 (K線 / 技術指標)</span>
                  </h3>
                  <p class="text-xs text-slate-400 mt-1">
                    使用前台 ECharts 繪製 • 數據包含 CDP、BBI、成交量、以及自選指標，共享 X 軸縮放
                  </p>
                </div>
                
                <!-- 指標選擇器 -->
                <div class="flex flex-wrap gap-2">
                  <button 
                    v-for="ind in [
                      { id: 'kd', name: 'KD 指標' },
                      { id: 'macd', name: 'MACD 柱狀' },
                      { id: 'dmi', name: 'DMI 動向' },
                      { id: 'bias', name: 'BIAS 乖離率' },
                      { id: 'williams', name: 'Williams %R' }
                    ]"
                    :key="ind.id"
                    @click="selectedIndicator = ind.id as any"
                    :class="[
                      'px-3 py-1.5 text-xs font-bold rounded-lg border transition-all cursor-pointer',
                      selectedIndicator === ind.id 
                        ? 'bg-cyan-500/20 text-cyan-400 border-cyan-500/40 shadow-sm' 
                        : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                    ]"
                  >
                    {{ ind.name }}
                  </button>
                </div>
              </div>

              <!-- ECharts 渲染畫布容器 -->
              <div class="relative w-full bg-slate-950/40 rounded-xl border border-slate-900 p-4">
                <div ref="taChartRef" class="w-full" style="height: 600px;"></div>
              </div>

              <!-- 圖表註解說明 -->
              <div class="mt-4 p-4 bg-slate-950/60 rounded-xl border border-slate-900/80 text-[11px] text-slate-400 leading-relaxed grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 class="font-bold text-slate-300 mb-1">📈 逆勢操作系統 CDP 說明：</h4>
                  <p>CDP (虛線) 代表當日合理中心值。AH/NH 為壓力點 (近高/最高)；NL/AL 為支撐點 (近低/最低)。用以研判當日強弱與逆勢買賣點。</p>
                  <h4 class="font-bold text-slate-300 mt-2 mb-1">📊 多空指標 BBI 說明：</h4>
                  <p>BBI (粉紅實線) 是 3、6、12、24 日移動平均線的綜合加權。收盤價在 BBI 之上為多頭市場；收盤價在 BBI 之下為空頭市場。</p>
                </div>
                <div>
                  <h4 class="font-bold text-slate-300 mb-1">🛠️ 技術指標計算區間說明：</h4>
                  <p>技術指標是基於您在後台配置的排程清單 (StockScheduleList) 中的 <code>analysis_period</code> (預設為前 3 年的歷史數據) 完整計算產出，圖表可透過滑動下方拉桿 (DataZoom) 來縮放查看指定期間數據。</p>
                </div>
              </div>

            </div>

          </div>

        </div>

        <!-- 初始無資料引導 -->
        <div v-else class="text-center py-20 bg-slate-900/20 backdrop-blur-sm border border-slate-900/50 rounded-2xl">
          <svg class="mx-auto h-12 w-12 text-slate-600 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
          </svg>
          <h3 class="text-slate-300 font-bold text-sm">尚未載入股票資料</h3>
          <p class="text-xs text-slate-500 mt-2 max-w-sm mx-auto leading-relaxed">
            請在上方輸入台股股票代碼（如 <span class="font-mono text-cyan-400 font-bold">2330</span>），並點擊「搜尋」獲取本機資料，或點擊「即時更新並儲存」啟動外部數據爬蟲。
          </p>
        </div>

      </section>

      <!-- ======================================================================= -->
      <!-- SECTION 2: 服務節點監控 (Health Monitor)                               -->
      <!-- ======================================================================= -->
      <section v-else-if="activeTab === 'health'" class="space-y-8">
        
        <!-- 健康狀態控制面板 -->
        <div class="glassmorphism rounded-2xl p-6 shadow-2xl border border-slate-900/50 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div>
            <h1 class="text-xl font-black text-slate-100 flex items-center space-x-2">
              <span>Containerization Stack 系統服務檢測</span>
            </h1>
            <p class="text-xs text-slate-400 mt-1">
              實時連線檢測 Django 5.2、MariaDB 12.3 與 Redis 8.8 快取的容器狀態
            </p>
          </div>
          
          <button 
            @click="fetchHealthStatus" 
            :disabled="healthLoading"
            class="px-5 py-2.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-bold rounded-xl transition-all duration-300 shadow-md shadow-cyan-500/20 shrink-0 cursor-pointer flex items-center space-x-2"
          >
            <svg v-if="healthLoading" class="animate-spin h-3.5 w-3.5 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>手動重新檢測</span>
          </button>
        </div>

        <!-- 3 大服務節點卡片 Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          <!-- 卡片 1: Django Backend -->
          <div class="glassmorphism rounded-2xl p-6 border border-slate-900/50 flex flex-col justify-between hover:border-slate-800 transition duration-300">
            <div>
              <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold uppercase tracking-wider text-cyan-400 bg-cyan-950/40 px-2.5 py-1 rounded-md border border-cyan-900/30">Django 5.2</span>
                <span class="flex h-2.5 w-2.5 relative">
                  <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                </span>
              </div>
              <h2 class="text-base font-bold text-slate-100">Django Backend</h2>
              <p class="text-[11px] text-slate-400 mt-2 leading-relaxed">
                Python 3.12 Web 應用伺服器。執行 REST API、Celery 背景佇列派發、與 Unfold 系統管理。
              </p>
            </div>
            <div class="mt-6 pt-4 border-t border-slate-800/60 text-[10px] text-slate-500">
              <div>狀態: <span class="text-emerald-400 font-semibold">運行中</span></div>
              <div class="mt-1">核心版本: <span class="text-slate-300 font-mono">{{ backendHealth ? 'Django ' + backendHealth.django_version : '載入中...' }}</span></div>
            </div>
          </div>

          <!-- 卡片 2: MariaDB Database -->
          <div class="glassmorphism rounded-2xl p-6 border border-slate-900/50 flex flex-col justify-between hover:border-slate-800 transition duration-300">
            <div>
              <div class="flex justify-between items-start mb-4">
                <span class="text-xs font-bold uppercase tracking-wider text-blue-400 bg-blue-950/40 px-2.5 py-1 rounded-md border border-blue-900/30">MariaDB 12.3</span>
                <span class="flex h-2.5 w-2.5 relative">
                  <span v-if="backendHealth && backendHealth.database.status === 'connected'" class="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span :class="[healthLoading ? 'bg-amber-500' : (backendHealth && backendHealth.database.status === 'connected') ? 'bg-emerald-500' : 'bg-rose-500']" class="relative inline-flex rounded-full h-2.5 w-2.5"></span>
                </span>
              </div>
              <h2 class="text-base font-bold text-slate-100">MariaDB Database</h2>
              <p class="text-[11px] text-slate-400 mt-2 leading-relaxed">
                多關聯式 SQL 資料庫。包含 `user_stock_db` 與 `db_employee` 多帳號隔離，掛載實體 `./db_data`。
              </p>
            </div>
            <div class="mt-6 pt-4 border-t border-slate-800/60 text-[10px] text-slate-500">
              <div>狀態: <span :class="[(backendHealth && backendHealth.database.status === 'connected') ? 'text-emerald-400' : 'text-rose-400']" class="font-semibold">{{ healthLoading ? '檢查中...' : (backendHealth && backendHealth.database.status === 'connected') ? '已連線' : '無連線' }}</span></div>
              <div class="mt-1">主機位置: <span class="text-slate-300 font-mono">fin-django-db:3306</span></div>
            </div>
          </div>

          <!-- 卡片 3: Redis Cache -->
          <div class="glassmorphism rounded-2xl p-6 border border-slate-900/50 flex flex-col justify-between hover:border-slate-800 transition duration-300">
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
                快取與 Session 記憶體伺服器。執行高併發快取儲存與 Celery Broker 調度，掛載實體 `./redis_data`。
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
/* Glassmorphism 玻璃擬態樣式 */
.glassmorphism {
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.04);
}
</style>

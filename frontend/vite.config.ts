/**
 * Vite 5 前端編譯與開發伺服器設定檔 (vite.config.ts)
 * 說明：整合 Vue 3.5、Tailwind CSS v4.3 插件，並將基礎路徑設為 /tech-stack/
 */
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  // 設定 Vue 前端開發伺服器與靜態資源之基礎路徑 (Base URL) 為 /tech-stack/
  base: '/tech-stack/',
  plugins: [
    vue(),        // 支援 Vue 3 SFC (Single File Component) 編譯
    tailwindcss() // 啟用 Tailwind CSS v4 高效能 CSS 引擎
  ],
  server: {
    host: '0.0.0.0', // 監聽所有網路介面以利 Docker 存取
    port: 5173,
    hmr: {
      path: '/tech-stack/_hmr', // 設定熱模組替換 WebSocket 轉接路徑
      clientPort: 80           // 指定 Client 端的 WebSocket 連線對外 Port (透過 Apache Port 80)
    },
    watch: {
      usePolling: true // 開啟輪詢模式，確保 Windows 掛載磁碟時能即時感應檔案修改
    }
  }
})

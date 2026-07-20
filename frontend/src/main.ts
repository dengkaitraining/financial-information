/**
 * Vue 3.5 應用程式主要進入點 (main.ts)
 * 說明：實例化 Vue App、載入全域 Tailwind 樣式，並掛載至 HTML 中的 #app 節點
 */
import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// 建立 Vue 應用實例並掛載至 #app
createApp(App).mount('#app')

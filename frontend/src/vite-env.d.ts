/**
 * Vite 與 Vue TypeScript 型態宣告檔 (vite-env.d.ts)
 * 說明：提供 Vite Client 型態參考以及 .vue 單檔案組件 (SFC) 之 TypeScript 型態宣告
 */

/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

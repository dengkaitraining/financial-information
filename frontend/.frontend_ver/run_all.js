import { fileURLToPath } from 'url';
import { testEnvironment } from './test_env.js';
import { testBackendApi } from './test_api.js';
import { testApacheProxy } from './test_web.js';

const __filename = fileURLToPath(import.meta.url);

async function main() {
  const showFrontendVer = process.env.SHOW_FRONTEND_VER !== 'False' && process.env.SHOW_FRONTEND_VER !== 'false';

  if (!showFrontendVer) {
    console.log("=".repeat(80));
    console.log("🔒 [安全防護] 正式上線模式已啟用。");
    console.log("👉 已依據控制參數 SHOW_FRONTEND_VER=False 隱蔽手動測試驗證資料 (frontend_ver)。");
    console.log("=".repeat(80));
    process.exit(0);
  }

  console.log("=".repeat(80));
  console.log("🚀 啟動 fin_vue_frontend 前端手動測試整合驗證程序");
  console.log("=".repeat(80));

  try {
    // 1. 執行開發環境檢查
    testEnvironment();
    console.log("\n");

    // 2. 執行 Django API 連線檢查
    await testBackendApi();
    console.log("\n");

    // 3. 執行 Apache Proxy 連線檢查
    await testApacheProxy();
    console.log("\n");

    console.log("=".repeat(80));
    console.log("🎉 所有前端手動測試驗證已順利完成！請檢閱上方詳細輸出以確認各服務狀態。");
    console.log("=".repeat(80));

  } catch (error) {
    console.error("\n🔴 執行前端手動測試驗證程序時發生未預期錯誤:", error);
    process.exit(1);
  }
}

main();

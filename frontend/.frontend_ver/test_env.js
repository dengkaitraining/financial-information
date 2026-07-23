import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export function testEnvironment() {
  console.log("=".repeat(60));
  console.log("🔍 啟動 Vue 3.5 前端開發環境與依賴驗證...");
  console.log("=".repeat(60));

  // 1. 輸出系統與版本資訊
  console.log("\n[步驟 1] 系統與版本資訊:");
  console.log(`  👉 Node.js 版本: ${process.version}`);
  console.log(`  👉 平台 (Platform): ${process.platform}`);
  console.log(`  👉 工作目錄: ${process.cwd()}`);

  // 2. 檢查環境變數
  console.log("\n[步驟 2] 重要環境變數設定:");
  const envVars = ['NODE_ENV', 'SHOW_FRONTEND_VER', 'HOST_OS'];
  for (const varName of envVars) {
    const val = process.env[varName] || '(未設定 / 預設值)';
    console.log(`  👉 ${varName}: ${val}`);
  }

  // 3. 讀取 package.json 並檢查 node_modules
  console.log("\n[步驟 3] 檢查 package.json 與依賴套件安裝狀態:");
  try {
    const packageJsonPath = path.resolve(__dirname, '../package.json');
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    console.log(`  👉 專案名稱: ${packageJson.name}`);
    console.log(`  👉 專案版本: ${packageJson.version}`);

    const checkDeps = {
      'dependencies': ['vue'],
      'devDependencies': ['vite', 'typescript', 'tailwindcss', '@tailwindcss/vite']
    };

    for (const [depType, deps] of Object.entries(checkDeps)) {
      console.log(`  👉 檢查 ${depType}:`);
      for (const dep of deps) {
        const declaredVer = packageJson[depType]?.[dep] || '未宣告';
        
        // 檢查 node_modules 下是否有該資料夾
        const nodeModulesPath = path.resolve(__dirname, `../node_modules/${dep}`);
        const exists = fs.existsSync(nodeModulesPath);
        
        if (exists) {
          console.log(`     ✓ [已安裝] ${dep} (宣告版本: ${declaredVer})`);
        } else {
          console.log(`     🔴 [未安裝] ${dep} (宣告版本: ${declaredVer}) - 請執行 npm install`);
        }
      }
    }
  } catch (error) {
    console.log(`🔴 讀取 package.json 失敗: ${error.message}`);
  }

  console.log("\n" + "=".repeat(60));
  console.log("✨ Vue 3.5 前端開發環境驗證完成。");
  console.log("=".repeat(60));
}

// 如果直接執行
if (process.argv[1] === __filename) {
  testEnvironment();
}

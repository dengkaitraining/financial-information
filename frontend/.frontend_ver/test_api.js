import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);

export async function testBackendApi() {
  console.log("=".repeat(60));
  console.log("🔍 啟動後端 Django REST API 連線驗證...");
  console.log("=".repeat(60));

  const apiUrl = process.env.BACKEND_API_URL || 'http://backend:8000/api/status/';
  console.log(`\n[步驟 1] 發送請求至後端 API 端點: ${apiUrl}`);

  try {
    const startTime = Date.now();
    const response = await fetch(apiUrl);
    const duration = Date.now() - startTime;

    console.log(`  👉 響應狀態碼 (Status): ${response.status} ${response.statusText}`);
    console.log(`  👉 響應耗時 (Latency): ${duration}ms`);

    if (response.ok) {
      const data = await response.json();
      console.log(`  👉 響應 JSON 數據:`);
      console.log(JSON.stringify(data, null, 2).split('\n').map(line => `     ${line}`).join('\n'));
      
      if (data.status === 'ok' || data.status === 'healthy' || data.status === 'success' || data.status === 'online') {
        console.log(`\n🟢 後端 API 連線與健康度測試成功！`);
      } else {
        console.log(`\n⚠️ 後端 API 響應不合預期，請檢查服務狀態。`);
      }
    } else {
      console.log(`\n🔴 後端 API 響應錯誤，狀態碼非 2xx 系列。`);
    }
  } catch (error) {
    console.log(`\n🔴 無法連線至後端 Django 服務 (${apiUrl})`);
    console.log(`   👉 錯誤原因: ${error.message}`);
    console.log(`   👉 說明: 請確保 fin_django_backend 容器正在運行且網路橋接正常。`);
  }

  console.log("\n" + "=".repeat(60));
  console.log("✨ 後端 Django REST API 連線驗證完成。");
  console.log("=".repeat(60));
}

// 如果直接執行
if (process.argv[1] === __filename) {
  testBackendApi();
}

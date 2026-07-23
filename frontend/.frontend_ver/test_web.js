import http from 'http';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);

function checkHttpLink(urlStr, hostHeader) {
  return new Promise((resolve, reject) => {
    const url = new URL(urlStr);
    const options = {
      method: 'GET',
      hostname: url.hostname,
      port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: url.pathname + url.search,
      headers: {}
    };
    if (hostHeader) {
      options.headers['Host'] = hostHeader;
    }
    const req = http.request(options, (res) => {
      resolve({ status: res.statusCode, statusText: res.statusMessage });
    });
    req.on('error', (err) => {
      reject(err);
    });
    req.end();
  });
}

export async function testApacheProxy() {
  console.log("=".repeat(60));
  console.log("🔍 啟動前端網頁伺服器與 Apache 反向代理連線驗證...");
  console.log("=".repeat(60));

  // 1. 驗證本機 Vite 開發伺服器埠號 (5173)
  const localUrl = 'http://localhost:5173/tech-stack/';
  console.log(`\n[步驟 1] 驗證本機 Vite 開發伺服器埠號: ${localUrl}`);
  try {
    const startTime = Date.now();
    const result = await checkHttpLink(localUrl);
    const duration = Date.now() - startTime;
    console.log(`  👉 響應狀態碼 (Status): ${result.status} ${result.statusText}`);
    console.log(`  👉 響應耗時 (Latency): ${duration}ms`);
    if (result.status >= 200 && result.status < 400) {
      console.log(`     ✓ 本機 Vite 開發伺服器運作正常！`);
    } else {
      console.log(`     🔴 本機 Vite 開發伺服器響應錯誤，狀態碼非 2xx/3xx 系列。`);
    }
  } catch (error) {
    console.log(`     🔴 無法直接連線至本機 Vite 服務 (${localUrl}): ${error.message}`);
  }

  // 2. 驗證 Apache 反向代理 (Port 80)
  const proxyUrl = process.env.APACHE_PROXY_URL || 'http://web:80/tech-stack/';
  console.log(`\n[步驟 2] 驗證 Apache 反向代理端點: ${proxyUrl}`);
  try {
    const startTime = Date.now();
    // 透過 Headers 傳入 Host: localhost，以繞過 Vite 的 Host Validation 限制 (403 Forbidden)
    const result = await checkHttpLink(proxyUrl, 'localhost');
    const duration = Date.now() - startTime;

    console.log(`  👉 響應狀態碼 (Status): ${result.status} ${result.statusText}`);
    console.log(`  👉 響應耗時 (Latency): ${duration}ms`);

    if (result.status >= 200 && result.status < 400) {
      console.log(`     ✓ Apache 反向代理轉接前端正常！`);
    } else {
      console.log(`     🔴 Apache 反向代理響應錯誤，狀態碼非 2xx/3xx 系列。`);
    }
  } catch (error) {
    console.log(`     🔴 無法連線至 Apache HTTPD 服務 (${proxyUrl}): ${error.message}`);
  }

  console.log("\n" + "=".repeat(60));
  console.log("✨ 前端網頁伺服器與 Apache 反向代理連線驗證完成。");
  console.log("=".repeat(60));
}

// 如果直接執行
if (process.argv[1] === __filename) {
  testApacheProxy();
}

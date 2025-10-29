// serve-with-node.cjs
const http = require("http");
const fs = require("fs");
const path = require("path");
const os = require("os");
const qrcode = require("qrcode-terminal");
const { execSync } = require("child_process");
const openBrowser = async (url) => {
  try {
    const open = (await import("open")).default;
    await open(url);
    console.log(`🎉 Opened ${url} in your browser`);
  } catch {
    if (os.platform() === "darwin") execSync(`open ${url}`);
    else if (os.platform() === "win32") execSync(`start ${url}`);
    else execSync(`xdg-open ${url}`);
  }
};

// --------------------- CONFIG --------------------- //
const DIST_DIR = path.resolve(__dirname, "dist");
const PORT = 5173;
const CONTROL_PORT = 4000; // <-- for Tkinter to send commands
const MAX_PORT_TRIES = 20;

// --------------------- UTIL --------------------- //
const getLocalIP = () => {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      if (iface.family === "IPv4" && !iface.internal) return iface.address;
    }
  }
  return "127.0.0.1";
};

async function checkPortForLAN(ip,port) {
  return new Promise((resolve) => {
    const server = http.createServer()
      .once("error", () => resolve(false))
      .once("listening", () => {
        server.close();
        resolve(true);
      })
      .listen(port, ip);
  });
}


const findAvailablePort = async (ip,startPort) => {
  let port = startPort;
  for (let i = 0; i < MAX_PORT_TRIES; i++) {
    if (await checkPortForLAN(ip,port)) return port;
    console.warn(`⚠️ Port ${port} is in use, trying next...`);
    port++;
  }
  throw new Error(`No available ports after ${MAX_PORT_TRIES} tries.`);
};

const mimeTypes = {
  ".html": "text/html",
  ".js": "application/javascript",
  ".mjs": "application/javascript",
  ".css": "text/css",
  ".json": "application/json",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".gif": "image/gif",
  ".svg": "image/svg+xml",
  ".ico": "image/x-icon",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ttf": "font/ttf",
  ".eot": "application/vnd.ms-fontobject",
  ".txt": "text/plain",
  ".wasm": "application/wasm",
};

// --------------------- SERVER --------------------- //
(async () => {
  const ip = getLocalIP();
  const port = await findAvailablePort(ip,PORT);
  const url = `http://${ip}:${port}`;

  console.log(`🌐 Serving static frontend from ${DIST_DIR}`);
  console.log(`🚀 Launching server at ${url}`);

  const server = http.createServer((req, res) => {
    let filePath = path.join(DIST_DIR, req.url.split("?")[0]);

    // If request is directory or root, serve index.html
    if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
      filePath = path.join(filePath, "index.html");
    }
    if (!fs.existsSync(filePath)) {
      res.writeHead(404, { "Content-Type": "text/plain" });
      return res.end("404 Not Found");
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = mimeTypes[ext] || "application/octet-stream";

    fs.readFile(filePath, (err, data) => {
      if (err) {
        res.writeHead(500, { "Content-Type": "text/plain" });
        return res.end("500 Internal Server Error");
      }
      res.writeHead(200, { "Content-Type": contentType });
      res.end(data);
    });
  });

  server.listen(port, "0.0.0.0", async () => {
    console.log(`✅ Server running!`);
    console.log(`📱 LAN URL: ${url}`);
    console.log(`💻 Localhost URL: http://localhost:${port}`);

    // 🔥 Print QR code to scan from your phone
    qrcode.generate(url, { small: true }, (qr) => {
      console.log(`\n📸 Scan this QR code to open on your phone:\n`);
      console.log(qr);
    });
    // Open browser automatically
    await openBrowser(url);

    console.log("Serving from:", DIST_DIR);
    
    // 🎯 Control server for Tkinter
    const controlServer = http.createServer(async (req, res) => {
      if (req.method === "POST" && req.url === "/open-browser") {
        await openBrowser(url);
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ success: true }));
      } else {
        res.writeHead(404);
        res.end();
      }
    });
    const controlServerIP = "127.0.0.1";
  const controlServerPort = await findAvailablePort(controlServerIP, 3069);
    controlServer.listen(controlServerPort, controlServerIP, () => {
    const url = `http://${controlServerIP}:${controlServerPort}/open-browser`;
    console.log(`🎮 Control server listening on port ${url}`);
  });

  });

})();

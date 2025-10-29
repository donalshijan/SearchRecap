// serve-with-ip.cjs
const { execSync, spawn } = require("child_process");
const address = require("./node_modules/address/dist/esm");
const http = require("http");
const os = require("os");

const ip = address.ip();
let port = 5173; // Vite’s default preview/serve port
const maxRetries = 20;

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

function getLocalIP() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      if (iface.family === "IPv4" && !iface.internal) {
        return iface.address; // e.g. 192.168.1.102
      }
    }
  }
  return "localhost";
}

async function findAvailablePort(ip,startPort) {
  let currentPort = startPort;
  for (let i = 0; i < maxRetries; i++) {
    const free = await checkPortForLAN(ip,currentPort);
    if (free) return currentPort;
    console.log(`⚠️ Port ${currentPort} is in use, trying another one...`);
    currentPort++;
  }
  throw new Error(`No free port found after ${maxRetries} tries.`);
}

(async () => {
  console.log(`🌐 Trying to serve static build on LAN starting at port ${port}...`);
  const ip = getLocalIP();
  const availablePort = await findAvailablePort(ip,port);
  const url = `http://${ip}:${availablePort}`;

  console.log(`✅ Serving static files from ./dist`);
  console.log(`🚀 Launching production build on ${url}`);

  // Spawn 'serve' (static file server)
  const child = spawn("npx", ["serve", "-s", "dist", "-l", `tcp://${ip}:${availablePort}`], {
    stdio: ["inherit", "pipe", "pipe"], // stdin, stdout, stderr
  });

  // Try to open in browser
// Wait for serve to actually start before opening browser
let opened = false;

child.stdout.on("data", async (data) => {
  process.stdout.write(data);

  const line = data.toString();
  if (!opened && /accepting connections|serving/i.test(line)) {
    opened = true;
    try {
      const open = (await import("open")).default;
      await open(url);
      console.log(`🎉 Opened ${url} in your browser`);
    } catch (err) {
      console.warn("⚠️ Could not open browser automatically.");
      if (os.platform() === "darwin") execSync(`open ${url}`);
      else if (os.platform() === "win32") execSync(`start ${url}`);
      else execSync(`xdg-open ${url}`);
    }
  }
});
})();

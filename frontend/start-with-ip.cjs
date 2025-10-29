const { exec } = require("child_process");
const address = require("./node_modules/address/dist/esm");

const ip = address.ip(); // Get local network IP
const port = 5173;       // Change this if your dev server uses another port
const url = `http://${ip}:${port}`;

console.log(`🌐 Will Try Launching dev server on LAN starting at http://${ip}:${port} ...`);

const command = `vite --host ${ip} --port ${port}`;

const child = exec(command);

let opened = false; // ensure we only open once

// Pipe Vite’s logs through
/* eslint-disable no-undef */
child.stdout.on("data",async (data) => { 
  process.stdout.write(data) 
  const match = data.toString().match(/http:\/\/[0-9.]+:(\d+)\//);
  if (match && !opened) {
    const actualPort = match[1];
    const url = `http://${ip}:${actualPort}`;
    opened = true;

    // 🪄 Open in browser
    console.log(`🚀 Opening ${url} in your browser...`);

    try {
      // Use dynamic import for ESM-only package
      const open = (await import("open")).default;
      await open(url);
      console.log(`✅ Dev server launched app at: ${url}`);
    } catch (err) {
      console.warn("⚠️ Could not use 'open' package, falling back to system command.");
      if (os.platform() === "darwin") exec(`open ${url}`);
      else if (os.platform() === "win32") exec(`start ${url}`);
      else exec(`xdg-open ${url}`);
    }
  }
});
child.stderr.on("data", (data) => process.stderr.write(data));

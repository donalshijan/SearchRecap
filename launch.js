#!/usr/bin/env node
/**
 * Launch script for backend + frontend servers.
 * Checks required files, spawns both servers, prefixes logs with color,
 * and gracefully handles shutdowns.
 */

const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");

// === Config ===
const backendCmd = ["python3",["-m","Backend.main",]];
const frontendBuildCmd = ["npm", ["run", "build"], { cwd: "Frontend" }];
const frontendServeCmd = ["npm", ["run", "serve"], { cwd: "Frontend" }];

const logsDir = path.join(process.cwd(), "logs");
if (!fs.existsSync(logsDir)) fs.mkdirSync(logsDir);

const backendLogPath = path.join(logsDir, "backend.log");
const frontendLogPath = path.join(logsDir, "frontend.log");

// === Colors ===
const colors = {
  reset: "\x1b[0m",
  magenta: "\x1b[35m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  red: "\x1b[31m",
  green: "\x1b[32m",
};

// === Utility functions ===
const log = (msg, color = colors.magenta) => {
  console.log(`${color}[Launcher]${colors.reset} ${msg}`);
};

const fileExists = (relPath) => fs.existsSync(path.join(process.cwd(), relPath));

const clearLogs = () => {
  [backendLogPath, frontendLogPath].forEach((file) => {
    try {
      fs.writeFileSync(file, "");
    } catch (err) {
      console.error(`Failed to clear ${file}:`, err.message);
    }
  });
};

const prefixStream = (stream, prefix, color, logFile) => {
  const fileStream = fs.createWriteStream(logFile, { flags: "a" });
  stream.on("data", (data) => {
    const lines = data.toString().split(/\r?\n/).filter(Boolean);
    for (const line of lines) {
      const prefixed = `${color}${prefix}${colors.reset} ${line}`;
      console.log(prefixed);
      fileStream.write(`${prefix} ${line}\n`);
    }
  });
};

// === Pre-checks ===
if (!fs.existsSync("Takeout")) {
  console.error(`${colors.red}❌ Takeout folder missing. Please ensure it exists in current directory.${colors.reset}`);
  process.exit(1);
}

const activityFile = path.join("Takeout", "My Activity", "Search", "MyActivity.json");
if (!fileExists(activityFile)) {
  console.error(`${colors.red}❌ MyActivity.json file not found at expected path: ${activityFile}${colors.reset}`);
  process.exit(1);
}

clearLogs();
log("✅ Pre-checks passed, launching servers...");

let backend = null;
let frontend = null;

/**
 * Spawns the backend and resolves when it emits the ready message.
 * If the backend exits early or timeout expires the promise rejects.
 *
 * @param {number} timeoutMs - how long to wait (ms) before rejecting (default 30000)
 */
const waitForBackendReady = (timeoutMs = 40000) => {
  return new Promise((resolve, reject) => {
    let ready = false;
    let timedOut = false;
    // spawn backend
    backend = spawn(backendCmd[0], backendCmd[1]);

    prefixStream(backend.stdout, "[Backend]", colors.blue, backendLogPath);
    prefixStream(backend.stderr, "[Backend]", colors.blue, backendLogPath);

    // listen for ready message on stdout
    const onData = (data) => {
      const lines = data.toString().split(/\r?\n/).filter(Boolean);
      for (const line of lines) {
        // print was handled by prefixStream; we still inspect content here
        if (!ready && line.startsWith("INFO:     Application startup complete.")) {
          ready = true;
          log("✅ Backend confirmed running!", colors.green);
          cleanup();
          return resolve();
        }
      }
    };

    // backend may emit on stdout/stderr; watch both (prefixStream already prints)
    backend.stdout.on("data", onData);
    backend.stderr.on("data", onData);

    // if backend exits before ready, reject
    backend.once("close", (code) => {
      if (ready) {
        log(`⚠️ Backend process exited with code ${code}`, colors.yellow);
        // If it had been ready earlier, we don't reject — the process later exited.
        return;
      }
      cleanup();
      reject(new Error(`Backend exited prematurely with code ${code}`));
    });

    // safety timeout
    const timeout = setTimeout(() => {
      timedOut = true;
      cleanup();
      // try to shut down backend if still running
      try { backend.kill("SIGINT"); } catch (_) {}
      reject(new Error(`Timed out waiting for backend ready after ${timeoutMs}ms`));
    }, timeoutMs);

    function cleanup() {
      clearTimeout(timeout);
      // remove listeners to avoid memory leaks
      try {
        backend.stdout.removeListener("data", onData);
        backend.stderr.removeListener("data", onData);
      } catch (_) {}
    }
  });
};


// === Graceful Shutdown ===
const shutdown = () => {
  log("🛑 Shutting down servers...");
  const attempts = 5;

  const killAndCheck = (proc, name, color) => {
    if (!proc || proc.killed) return Promise.resolve(true);
    proc.kill("SIGINT");

    return new Promise((resolve) => {
      let tries = 0;
      const interval = setInterval(() => {
        tries++;
        if (proc.killed) {
          clearInterval(interval);
          console.log(`${color}✅ ${name} terminated successfully.${colors.reset}`);
          resolve(true);
        } else if (tries >= attempts) {
          clearInterval(interval);
          console.error(`${colors.red}❌ Failed to terminate ${name} after ${attempts} attempts.${colors.reset}`);
          resolve(false);
        }
      }, 1000);
    });
  };

  Promise.all([
    killAndCheck(backend, "Backend", colors.blue),
    killAndCheck(frontend, "Frontend", colors.yellow),
  ]).then(() => {
    log("👋 Exiting launcher.");
    process.exit(0);
  });
};



// === Main async flow ===
(async () => {
  try {

    // === Launch backend ===
    log("🚀 Starting Backend...");
    await waitForBackendReady(30_000); // 30s timeout (adjust if needed)

    // === Build frontend ===
    log("🏗️ Building Frontend...");
    const build = spawn(frontendBuildCmd[0], frontendBuildCmd[1], frontendBuildCmd[2]);
    prefixStream(build.stdout, "[Frontend]", colors.yellow, frontendLogPath);
    prefixStream(build.stderr, "[Frontend]", colors.yellow, frontendLogPath);

    build.on("close", (code) => {
    if (code !== 0) {
        console.error(`${colors.red}❌ Frontend build failed with exit code ${code}${colors.reset}`);
        backend.kill("SIGINT");
        process.exit(1);
    }

    // === Serve frontend after successful build ===
    log("🌐 Starting Frontend...");
    frontend = spawn(frontendServeCmd[0], frontendServeCmd[1], frontendServeCmd[2]);
    prefixStream(frontend.stdout, "[Frontend]", colors.yellow, frontendLogPath);
    prefixStream(frontend.stderr, "[Frontend]", colors.yellow, frontendLogPath);
    frontend.on("close", (code) => log(`⚠️ Frontend process exited with code ${code}`));
    });

    // === Graceful Shutdown ===


    process.on("SIGINT", shutdown);
    process.on("SIGTERM", shutdown);
  } catch (err) {
    console.error(`${colors.red}❌ Launcher error: ${err.message}${colors.reset}`);
    // ensure child procs are killed
    try { if (backend) backend.kill("SIGINT"); } catch (_) {}
    try { if (frontend) frontend.kill("SIGINT"); } catch (_) {}
    process.exit(1);
  }
})();
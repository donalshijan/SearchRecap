async function getStorage() {
  return await chrome.storage.local.get(["logging_enabled", "device_id", "user_name", "device_name"]);
}

async function setStorage(data) {
  return await chrome.storage.local.set(data);
}

async function getBrowserInfo() {
  const ua = navigator.userAgent || "";

  if (navigator.brave && await navigator.brave.isBrave()) {
    const braveMatch = ua.match(/Chrome\/([\d.]+)/);
    return `Brave-${braveMatch ? braveMatch[1] : "unknown"}`;
  }

  const chromeMatch = ua.match(/Chrome\/([\d.]+)/);
  if (chromeMatch) return `Chrome-${chromeMatch[1]}`;

  const firefoxMatch = ua.match(/Firefox\/([\d.]+)/);
  if (firefoxMatch) return `Firefox-${firefoxMatch[1]}`;

  const safariMatch = ua.match(/Version\/([\d.]+).*Safari/);
  if (safariMatch) return `Safari-${safariMatch[1]}`;

  // fallback
  return `Unknown-${(ua.split(" ")[0] || "browser")}`;
}

async function getPlatform() {
  if (navigator.userAgentData) {
    const data = await navigator.userAgentData.getHighEntropyValues(["platform"]);
    return data.platform || "Unknown";
  } else {
    // fallback for older browsers
    const ua = navigator.userAgent.toLowerCase();
    if (ua.includes("win")) return "Windows";
    if (ua.includes("mac")) return "macOS";
    if (ua.includes("linux")) return "Linux";
    if (ua.includes("android")) return "Android";
    if (ua.includes("iphone") || ua.includes("ipad")) return "iOS";
    return "Unknown";
  }
}

async function registerDevice(user, device) {
  const platform = getPlatform();
  const browser = getBrowserInfo();

  const res = await fetch("http://192.168.1.88:8000/devices/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user, name: device, platform, browser })
  });

  const data = await res.json();
  await setStorage({ device_id: data.device_id, user_name: user, device_name: device });
  return data.device_id;
}

async function updateUI() {
  const { logging_enabled, device_id, user_name, device_name } = await getStorage();
  const status = document.getElementById("status");
  const toggleBtn = document.getElementById("toggleBtn");
  const form = document.getElementById("form");

  if (!device_id) {
    status.innerText = "⚙️ No device registered.";
    form.style.display = "block";
    toggleBtn.style.display = "none";
  } else {
    form.style.display = "none";
    toggleBtn.style.display = "inline-block";
    if (logging_enabled) {
      status.innerText = `🟢 Logging active as ${user_name} (${device_name})`;
      toggleBtn.innerText = "Stop Logging";
    } else {
      status.innerText = `🔴 Logging stopped`;
      toggleBtn.innerText = "Start Logging";
    }
  }
}

document.getElementById("registerBtn")?.addEventListener("click", async () => {
  const user = document.getElementById("user").value.trim();
  const device = document.getElementById("device").value.trim();
  if (!user || !device) return alert("Please fill both fields.");

  await registerDevice(user, device);
  await updateUI();
});

document.getElementById("toggleBtn")?.addEventListener("click", async () => {
  const { logging_enabled } = await getStorage();
  await setStorage({ logging_enabled: !logging_enabled });
  await updateUI();
  const msg = !logging_enabled ? "enabled" : "disabled";
  console.log(`Logging ${msg}`);
});

updateUI();

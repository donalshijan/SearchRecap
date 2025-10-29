// Storage management
async function getStorage() {
  return await chrome.storage.local.get(["logging_enabled", "device_id", "user_name", "device_name", "backend_url"]);
}

async function setStorage(data) {
  return await chrome.storage.local.set(data);
}

// Backend URL management
async function getBackendUrl() {
  const { backend_url } = await getStorage();
  return backend_url || "";
}

async function testBackendConnection(url) {
  try {
    const response = await fetch(`${url}/ping`);
    if (response.ok) {
      const data = await response.json();
      return data.status === "ok";
    }
    return false;
  } catch (error) {
    console.error("Connection test failed:", error);
    return false;
  }
}

async function validateDevice(backendUrl, deviceId) {
  try {
    const response = await fetch(`${backendUrl}/validate-device/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ device_id: deviceId })
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data.status === "valid") {
        return { valid: true, reason: "valid" };
      } else {
        return { valid: false, reason: "invalid_device" };
      }
    }
    return { valid: false, reason: "server_error" };
  } catch (error) {
    console.error("Device validation failed:", error);
    return { valid: false, reason: "server_unreachable" };
  }
}

// Browser and platform detection
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

  return `Unknown-${(ua.split(" ")[0] || "browser")}`;
}

async function getPlatform() {
  if (navigator.userAgentData) {
    const data = await navigator.userAgentData.getHighEntropyValues(["platform"]);
    return data.platform || "Unknown";
  } else {
    const ua = navigator.userAgent.toLowerCase();
    if (ua.includes("win")) return "Windows";
    if (ua.includes("mac")) return "macOS";
    if (ua.includes("linux")) return "Linux";
    if (ua.includes("android")) return "Android";
    if (ua.includes("iphone") || ua.includes("ipad")) return "iOS";
    return "Unknown";
  }
}

// Device registration
async function registerDevice(user_name, device_name) {
  const backendUrl = await getBackendUrl();
  if (!backendUrl) {
    throw new Error("Backend URL not configured");
  }

  const platform = await getPlatform();
  const browser = await getBrowserInfo();

  const res = await fetch(`${backendUrl}/devices/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_name, device_name, platform, browser })
  });

  if (!res.ok) {
    throw new Error(`Failed to register device: ${res.status}`);
  }

  const data = await res.json();
  await setStorage({ device_id: data.device_id, user_name: user_name, device_name: device_name });
  return data.device_id;
}

// UI Management
async function updateUI() {
  const { logging_enabled, device_id, user_name, device_name, backend_url } = await getStorage();
  const status = document.getElementById("status");
  const backendConfig = document.getElementById("backendConfig");
  const backendReset = document.getElementById("backendReset");
  const form = document.getElementById("form");
  const toggleBtn = document.getElementById("toggleBtn");
  const backendUrlInput = document.getElementById("backendUrl");

  // Show backend URL input if not configured
  if (!backend_url) {
    status.innerText = "Please configure backend URL first";
    backendConfig.style.display = "block";
    backendReset.style.display = "none";
    form.style.display = "none";
    toggleBtn.style.display = "none";
    return;
  }

  // Backend URL is configured, show reset button and hide config
  backendConfig.style.display = "none";
  backendReset.style.display = "block";
  backendUrlInput.value = backend_url;

  // Check if device is registered and validate it
  if (!device_id) {
    status.innerText = "Backend connected. Please register device.";
    form.style.display = "block";
    toggleBtn.style.display = "none";
  } else {
    // Validate existing device_id with backend
    status.innerText = "Validating device...";
    const validationResult = await validateDevice(backend_url, device_id);
    
    if (validationResult.valid) {
      // Device is valid, show logging controls
      form.style.display = "none";
      toggleBtn.style.display = "inline-block";
      if (logging_enabled) {
        status.innerText = `Logging started from ${user_name}'s (${device_name})`;
        toggleBtn.innerText = "Stop Logging";
      } else {
        status.innerText = `Logging stopped`;
        toggleBtn.innerText = "Start Logging";
      }
    } else if (validationResult.reason === "invalid_device") {
      // Device is invalid, clear it and show registration form
      await setStorage({ device_id: "", user_name: "", device_name: "" });
      status.innerText = "Device not found in database. Please re-register.";
      form.style.display = "block";
      toggleBtn.style.display = "none";
    } else {
      // Server is unreachable or error - keep device info but disable logging
      status.innerText = "Server unreachable. Device info preserved.";
      form.style.display = "none";
      toggleBtn.style.display = "inline-block";
      toggleBtn.innerText = "Start Logging";
      toggleBtn.disabled = true;
      // Disable logging if it was enabled
      if (logging_enabled) {
        await setStorage({ logging_enabled: false });
      }
    }
  }
}

// Event Listeners
document.getElementById("testConnectionBtn")?.addEventListener("click", async () => {
  const url = document.getElementById("backendUrl").value.trim();
  const connectionStatus = document.getElementById("connectionStatus");
  
  if (!url) {
    connectionStatus.innerText = "Please enter a URL";
    return;
  }

  connectionStatus.innerText = "Testing connection...";
  
  const isValid = await testBackendConnection(url);
  if (isValid) {
    connectionStatus.innerText = "Connected successfully!";
    await setStorage({ backend_url: url });
    setTimeout(updateUI, 1000); // Update UI after a short delay
  } else {
    connectionStatus.innerText = "Connection failed. Check URL and server status.";
  }
});

document.getElementById("registerBtn")?.addEventListener("click", async () => {
  const user = document.getElementById("user").value.trim();
  const device = document.getElementById("device").value.trim();
  
  if (!user || !device) {
    alert("Please fill both fields.");
    return;
  }

  try {
    await registerDevice(user, device);
    await updateUI();
  } catch (error) {
    alert(`Registration failed: ${error.message}`);
  }
});

document.getElementById("toggleBtn")?.addEventListener("click", async () => {
  const { logging_enabled, backend_url, device_id } = await getStorage();
  
  // If trying to start logging, check server first
  if (!logging_enabled && backend_url && device_id) {
    status.innerText = "Checking server connection...";
    const validationResult = await validateDevice(backend_url, device_id);
    console.log('hello1');
    if (!validationResult.valid) {
      console.log('hello');
      status.innerText = "Server unreachable. Device info preserved.";
      return;
    }
    else{
      console.log('hello3');
      await setStorage({ logging_enabled: true });
      await updateUI();
      console.log(`Logging enabled`);
      return;
    }
  }
  
  await setStorage({ logging_enabled: !logging_enabled });
  await updateUI();
  const msg = !logging_enabled ? "enabled" : "disabled";
  console.log(`Logging ${msg}`);
});

document.getElementById("resetBackendBtn")?.addEventListener("click", async () => {
  if (confirm("Are you sure you want to reset the backend URL? This will require reconfiguration.")) {
    await setStorage({ backend_url: "" });
    await updateUI();
  }
});



// Initialize UI
updateUI();

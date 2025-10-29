async function getStorage() {
  return await chrome.storage.local.get(["logging_enabled", "device_id", "backend_url"]);
}

async function getBackendUrl() {
  const { backend_url } = await getStorage();
  return backend_url || "";
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

async function sendQueryToBackend(query, device_id) {
  const backendUrl = await getBackendUrl();
  if (!backendUrl) {
    console.error("Backend URL not configured");
    return;
  }

  // Validate device before sending event
  const validationResult = await validateDevice(backendUrl, device_id);
  if (!validationResult.valid) {
    if (validationResult.reason === "invalid_device") {
      console.warn("Device validation failed - device not found, clearing stored device info");
      await chrome.storage.local.set({ device_id: "", user_name: "", device_name: "", logging_enabled: false });
    } else {
      console.warn("Server unreachable, disabling logging but preserving device info");
      await chrome.storage.local.set({ logging_enabled: false });
      await updateIcon();
      // Show notification to user about server being down
      showServerDownNotification();
    }
    return;
  }

  const payload = {
    query,
    timestamp: new Date().toISOString(),
    device_id,
  };

  try {
    const res = await fetch(`${backendUrl}/events/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    console.log("✅ Event sent successfully:", query);
  } catch (err) {
    console.error("Failed to send query:", err);
  }
}

let lastQuery = null;

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  // trying to match patterns
  // http://www.google.com/search
  // https://google.co.in/search
  // https://www.google.co.uk/search

  if (changeInfo.url && /https?:\/\/(www\.)?google\.[^/]+\/search/.test(changeInfo.url)){
    const params = new URL(changeInfo.url).searchParams;
    const query = params.get("q");
    if (!query || query === lastQuery) return; // prevent duplicates
    lastQuery = query;

    const { logging_enabled, device_id, backend_url } = await getStorage();
    if (logging_enabled && device_id && backend_url) {
      console.log("Captured query:", query);
      await sendQueryToBackend(query, device_id);
    } else if (logging_enabled && device_id && !backend_url) {
      console.warn("Logging enabled but backend URL not configured");
    }
  }
});

chrome.runtime.onInstalled.addListener(() => {
  console.log("Background script loaded and ready to capture Google searches!");
});

let currentIconPath = 'icons/off.png'; // cache last applied icon path

async function updateIcon() {
  const { logging_enabled, backend_url } = await chrome.storage.local.get(["logging_enabled", "backend_url"]);
  
  // Show off icon if backend not configured or logging disabled
  const iconPath = (logging_enabled && backend_url) ? "icons/on.png" : "icons/off.png";

  // ✅ Skip redundant update
  if (iconPath === currentIconPath) return;

  // ✅ Apply new icon and cache it
  await chrome.action.setIcon({ path: iconPath });
  currentIconPath = iconPath;
}

// Call on startup or extension load
chrome.runtime.onStartup.addListener(updateIcon);
chrome.runtime.onInstalled.addListener(updateIcon);

// Listen for changes in chrome.storage and update dynamically
chrome.storage.onChanged.addListener(async (changes, area) => {
  if (area === "local" && (changes.logging_enabled || changes.backend_url)) {
    await updateIcon();
  }
});

// Function to show server down notification
async function showServerDownNotification() {
  try {
    // Get the current active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    if (!tab) return;
    
    // Inject CSS and HTML for the modal
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: injectServerDownModal
    });
  } catch (error) {
    console.error("Failed to show server down notification:", error);
  }
}

// Function to be injected into the page to show the modal
function injectServerDownModal() {
  // Check if modal already exists
  if (document.getElementById('search-logger-modal')) {
    return;
  }
  
  // Create modal HTML
  const modalHTML = `
    <div id="search-logger-modal" style="
      position: fixed;
      top: 20px;
      right: 20px;
      background: linear-gradient(135deg, #ff6b6b, #ee5a52);
      color: white;
      padding: 16px 20px;
      border-radius: 12px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
      z-index: 10000;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 14px;
      font-weight: 500;
      max-width: 320px;
      opacity: 1;
      transform: translateX(0);
      transition: all 0.3s ease-out;
      border: 1px solid rgba(255, 255, 255, 0.2);
    ">
      <div style="
        display: flex;
        align-items: center;
        gap: 12px;
      ">
        <div style="
          width: 24px;
          height: 24px;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 16px;
        ">
          ⚠️
        </div>
        <div>
          <div style="font-weight: 600; margin-bottom: 4px;">
            Search Logging Stopped
          </div>
          <div style="font-size: 12px; opacity: 0.9;">
            Server connection lost. Click extension to reconnect.
          </div>
        </div>
      </div>
    </div>
  `;
  
  // Add modal to page
  document.body.insertAdjacentHTML('beforeend', modalHTML);
  
  // Auto-hide modal after 5 seconds with fade-out animation
  setTimeout(() => {
    const modal = document.getElementById('search-logger-modal');
    if (modal) {
      modal.style.opacity = '0';
      modal.style.transform = 'translateX(100%)';
      
      // Remove modal from DOM after animation completes
      setTimeout(() => {
        modal.remove();
      }, 300);
    }
  }, 5000);
}
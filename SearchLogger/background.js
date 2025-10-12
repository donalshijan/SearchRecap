async function getStorage() {
  return await chrome.storage.local.get(["logging_enabled", "device_id"]);
}

async function sendQueryToBackend(query, device_id) {
  const payload = {
    query,
    timestamp: new Date().toISOString(),
    device_id,
  };

  try {
    const res = await fetch("http://192.168.1.88:8000/events/", {
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

    const { logging_enabled, device_id } = await getStorage();
    if (logging_enabled && device_id) {
      console.log("Captured query:", query);
      await sendQueryToBackend(query, device_id);
    }
  }
});

chrome.runtime.onInstalled.addListener(() => {
  console.log("Background script loaded and ready to capture Google searches!");
});

let currentIconPath = 'icons/off.png'; // cache last applied icon path

async function updateIcon() {
  const { logging_enabled } = await chrome.storage.local.get("logging_enabled");
  const iconPath = logging_enabled ? "icons/on.png" : "icons/off.png";

  // ✅ Skip redundant update
  if (iconPath === currentIconPath) return;

  // ✅ Apply new icon and cache it
  await chrome.action.setIcon({ path: iconPath });
  currentIconPath = iconPath;
}

async function updateIcon() {
  const { logging_enabled } = await chrome.storage.local.get("logging_enabled");
  const iconPath = logging_enabled ? "icons/on.png" : "icons/off.png";
  await chrome.action.setIcon({ path: iconPath });
}

// Call on startup or extension load
chrome.runtime.onStartup.addListener(updateIcon);
chrome.runtime.onInstalled.addListener(updateIcon);

// Listen for changes in chrome.storage and update dynamically
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === "local" && changes.logging_enabled) {
    updateIcon();
  }
});
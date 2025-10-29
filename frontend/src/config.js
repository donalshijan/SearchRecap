// This mirrors the context, but for non-React files like api.js
export const getBackendUrl = () => localStorage.getItem("backendUrl") || "";

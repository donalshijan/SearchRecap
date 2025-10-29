import React, { createContext, useState, useEffect } from "react";

// Create context
const ConfigContext = createContext(null);

// Hook for components


export const ConfigProvider = ({ children }) => {
  const [backendUrl, setBackendUrl] = useState(localStorage.getItem("backendUrl") || "");

  // Persist changes to localStorage
  useEffect(() => {
    if (backendUrl) {
      localStorage.setItem("backendUrl", backendUrl);
    }
  }, [backendUrl]);

  const value = { backendUrl, setBackendUrl };

  return (
    <ConfigContext.Provider value={value}>
      {children}
    </ConfigContext.Provider>
  );
};

export default ConfigContext;

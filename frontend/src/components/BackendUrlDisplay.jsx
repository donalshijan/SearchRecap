import React from "react";
import { useConfig } from "../hooks/useConfig";

export default function BackendUrlDisplay() {
  const { backendUrl, setBackendUrl } = useConfig();

  const handleReset = () => {
    if (window.confirm("Are you sure you want to reset the backend URL? This will require reconfiguration.")) {
      setBackendUrl("");
    }
  };

  return (
    <div className="backend-url-display">
      <div className="backend-info">
        <span className="backend-label">Backend:</span>
        <span className="backend-url">{backendUrl}</span>
      </div>
      <button 
        className="reset-backend-btn" 
        onClick={handleReset}
        title="Reset Backend URL"
      >
        Reset
      </button>
    </div>
  );
}


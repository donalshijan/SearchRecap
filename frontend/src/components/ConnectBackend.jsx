import React, { useState } from "react";
import { useConfig } from "../hooks/useConfig";

export default function ConnectBackend() {
  const { setBackendUrl } = useConfig();
  const [backendUrl, setBackendUrlLocal] = useState("");
  const [status, setStatus] = useState("");

  const testConnection = async () => {
    try {
      setStatus("Testing connection...");
      const res = await fetch(`${backendUrl}/ping`);
      if (res.ok) {
        const data = await res.json();
        if (data.status === "ok") {
          setStatus("Connected successfully!");
          setBackendUrl(backendUrl);
        } else {
          setStatus("Unexpected response from server.");
        }
      } else {
        setStatus("Server unreachable or invalid response.");
      }
    } catch (err) {
      setStatus("Could not connect. Check IP or server status.");
      console.error(err);
    }
  };

  return (
    <div className="connect-backend-container">
      <h2>Connect to Backend Server</h2>
      <input
        type="text"
        placeholder="Enter backend URL (e.g. http://192.168.0.105:8000)"
        value={backendUrl}
        onChange={(e) => setBackendUrlLocal(e.target.value)}
      />
      <button onClick={testConnection}>Test & Connect</button>
      {status && <p className="status-message">{status}</p>}
    </div>
  );
}

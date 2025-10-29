import React, { useState, useEffect } from "react";
import Tabs from "./components/Tabs";
import Dashboard from "./pages/Dashboard";
import Flashcards from "./pages/Flashcards";
import ThemeToggle from "./components/ThemeToggle";
import ConnectBackend from "./components/ConnectBackend";
import BackendUrlDisplay from "./components/BackendUrlDisplay";
import { useConfig } from "./hooks/useConfig";
export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [theme, setTheme] = useState(localStorage.getItem("theme") || "light");
  const { backendUrl } = useConfig();

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const renderTab = () => {
    switch (activeTab) {
      case "dashboard":
        return <Dashboard />;
      case "flashcards":
        return (
            <Flashcards />
        );
      default:
        return <Dashboard />;
    }
  };

  if (!backendUrl) {
    return <ConnectBackend />;
  }

  return (
    <div className="app-container">
      <header className="header">
        <Tabs active={activeTab} onChange={setActiveTab} />
        <ThemeToggle theme={theme} setTheme={setTheme} />
      </header>
      <main className="main-content">{renderTab()}</main>
      <footer className="app-footer">
        <BackendUrlDisplay />
      </footer>
    </div>
  );
}

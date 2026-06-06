import { useState, useEffect } from "react";
import { CharacterSheet } from "./components/CharacterSheet";
import { GameBoard } from "./components/GameBoard";
import { LoadingScreen } from "./components/LoadingScreen";
import { useBackend } from "./hooks/useBackend";
import { useGameEngine } from "./hooks/useGameEngine";
import "./App.css";

function App() {
  const { isRunning, loading: backendLoading, error: backendError } = useBackend();
  const { loading: actionLoading, error: actionError, performAction } = useGameEngine();
  const [activeModel, setActiveModel] = useState("gpt-4o-mini");

  useEffect(() => {
    if (isRunning) {
      fetch("http://localhost:8000/model/active")
        .then((res) => res.json())
        .then((data) => {
          if (data.active_model) {
            setActiveModel(data.active_model);
          }
        })
        .catch((err) => console.error("Error fetching active model:", err));
    }
  }, [isRunning]);

  const handleModelChange = async (modelName: string) => {
    try {
      const res = await fetch("http://localhost:8000/model/active", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model: modelName }),
      });
      if (res.ok) {
        const data = await res.json();
        setActiveModel(data.active_model);
      }
    } catch (err) {
      console.error("Error setting active model:", err);
    }
  };

  if (backendLoading) {
    return <LoadingScreen message="Initializing Backend..." error={backendError} />;
  }

  if (!isRunning) {
    return (
      <LoadingScreen
        message="Backend Unavailable"
        error={backendError || "Failed to connect to backend services"}
      />
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>CRIPTA</h1>
          <span className="tagline">Virtual Dungeon Master - D&D 5.5</span>
        </div>
        <div className="header-status">
          <div className="model-selector-container">
            <label htmlFor="model-select">Model:</label>
            <select
              id="model-select"
              value={activeModel}
              onChange={(e) => handleModelChange(e.target.value)}
              className="model-select-dropdown"
            >
              <option value="gpt-4o-mini">GPT-4o-mini (OpenAI)</option>
              <option value="gpt-4o">GPT-4o (OpenAI)</option>
              <option value="qwen2.5:1.5b">Qwen2.5:1.5b (Ollama)</option>
              <option value="llama3">Llama 3 (Ollama)</option>
            </select>
          </div>
          <span className="status-indicator ready">Backend Ready</span>
        </div>
      </header>

      <main className="app-main">
        <aside className="sidebar">
          <div className="sidebar-content">
            <CharacterSheet />
            <div className="sidebar-section">
              <h3>Quick Commands</h3>
              <div className="command-buttons">
                <button onClick={() => performAction("combat", "Attack")} disabled={actionLoading}>
                  Attack
                </button>
                <button
                  onClick={() => performAction("exploration", "Look around")}
                  disabled={actionLoading}
                >
                  Search
                </button>
              </div>
            </div>
          </div>
        </aside>

        <section className="main-content">
          <GameBoard onAction={performAction} loading={actionLoading} />
          {actionError && (
            <div className="error-banner">
              <span>{actionError}</span>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;

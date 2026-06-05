import React from "react";
import { GameBoard } from "./components/GameBoard";
import { CharacterSheet } from "./components/CharacterSheet";
import { LoadingScreen } from "./components/LoadingScreen";
import { useBackend } from "./hooks/useBackend";
import { useGameEngine } from "./hooks/useGameEngine";
import "./App.css";

function App() {
  const { isRunning, loading: backendLoading, error: backendError } = useBackend();
  const { loading: actionLoading, error: actionError, performAction } = useGameEngine();

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
          <h1>🧙‍♂️ CRIPTA</h1>
          <span className="tagline">Virtual Dungeon Master - D&D 5.5</span>
        </div>
        <div className="header-status">
          <span className="status-indicator ready">● Backend Ready</span>
        </div>
      </header>

      <main className="app-main">
        <aside className="sidebar">
          <div className="sidebar-content">
            <CharacterSheet />
            <div className="sidebar-section">
              <h3>Quick Commands</h3>
              <div className="command-buttons">
                <button onClick={() => performAction("combat", "Attack")}
                  disabled={actionLoading}>
                  ⚔️ Attack
                </button>
                <button onClick={() => performAction("exploration", "Look around")}
                  disabled={actionLoading}>
                  🔍 Search
                </button>
              </div>
            </div>
          </div>
        </aside>

        <section className="main-content">
          <GameBoard onAction={performAction} loading={actionLoading} />
          {actionError && (
            <div className="error-banner">
              <span>⚠️ {actionError}</span>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;

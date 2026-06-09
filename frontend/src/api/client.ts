import { invoke } from "@tauri-apps/api/core";

const BACKEND_URL = "http://localhost:8000";

export async function startDockerBackend(): Promise<string> {
  try {
    if (window.__TAURI_INTERNALS__) {
      const result = await invoke<string>("start_docker_backend");
      console.log("✅ Docker started:", result);
      return result;
    }
    console.log("Not in Tauri, skipping Docker start");
    return "Skipped";
  } catch (error) {
    console.error("❌ Error starting Docker:", error);
    throw error;
  }
}

export async function stopDockerBackend(): Promise<string> {
  try {
    if (window.__TAURI_INTERNALS__) {
      const result = await invoke<string>("stop_docker_backend");
      console.log("✅ Docker stopped:", result);
      return result;
    }
    console.log("Not in Tauri, skipping Docker stop");
    return "Skipped";
  } catch (error) {
    console.error("❌ Error stopping Docker:", error);
    throw error;
  }
}

export async function processAction(action: {
  action_type: string;
  description: string;
  character_id?: string;
}) {
  const res = await fetch(`${BACKEND_URL}/action`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(action),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function rollDice(notation: string) {
  const res = await fetch(`${BACKEND_URL}/dice/roll?notation=${encodeURIComponent(notation)}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export async function getGameStatus() {
  const res = await fetch(`${BACKEND_URL}/status`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}



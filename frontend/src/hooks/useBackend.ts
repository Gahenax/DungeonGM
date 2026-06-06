import { useState, useEffect } from "react";
import { startDockerBackend, stopDockerBackend, getGameStatus } from "../api/client";

export function useBackend() {
  const [isRunning, setIsRunning] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function initialize() {
      try {
        setLoading(true);
        await startDockerBackend();
        
        // Wait for services to be ready
        await new Promise(resolve => setTimeout(resolve, 3000));
        
        await getGameStatus();
        setIsRunning(true);
        setError(null);
      } catch (err) {
        console.error("Failed to start backend:", err);
        setError(String(err));
        setIsRunning(false);
      } finally {
        setLoading(false);
      }
    }

    initialize();

    return () => {
      stopDockerBackend().catch(console.error);
    };
  }, []);

  return { isRunning, loading, error };
}

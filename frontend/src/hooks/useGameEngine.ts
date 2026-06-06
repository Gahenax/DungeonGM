import { useCallback, useState } from "react";
import { processAction } from "../api/client";

interface RoomState {
  id: string;
  name: string;
  description: string;
  clue?: string;
}

interface CharacterState {
  hp_current?: number;
  hp_max?: number;
  ac?: number;
  level?: number;
}

interface GameState {
  hp: number;
  maxHp: number;
  ac: number;
  level: number;
  room?: RoomState;
  character?: CharacterState;
}

export interface ActionResult {
  success: boolean;
  message: string;
  narrative: string;
  game_state?: Partial<GameState>;
  available_actions?: string[];
  generated_events?: Array<Record<string, unknown>>;
}

export function useGameEngine() {
  const [gameState, setGameState] = useState<GameState>({
    hp: 10,
    maxHp: 10,
    ac: 10,
    level: 1,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const performAction = useCallback(
    async (actionType: string, description: string): Promise<ActionResult | null> => {
      setLoading(true);
      setError(null);
      try {
        const result = await processAction({
          action_type: actionType,
          description,
          character_id: "player_1",
        });
        if (result.game_state) {
          setGameState((prev) => ({ ...prev, ...result.game_state }));
        }
        return result;
      } catch (err) {
        const errorMsg = String(err);
        setError(errorMsg);
        return null;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  return { gameState, loading, error, performAction };
}

import React, { useEffect, useRef, useState } from "react";
import type { ActionResult } from "../hooks/useGameEngine";
import "./GameBoard.css";

interface ChatMessage {
  id: string;
  role: "narrator" | "player";
  text: string;
  timestamp: Date;
}

interface GameBoardProps {
  onAction: (actionType: string, description: string) => Promise<ActionResult | null>;
  loading: boolean;
}

export function GameBoard({ onAction, loading }: GameBoardProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "1",
      role: "narrator",
      text: "You awaken in a dark chamber. Torchlight flickers against ancient stone. The air is cold and still.",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [selectedAction, setSelectedAction] = useState<string>("combat");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || loading) return;

    const playerText = inputValue;
    const playerMsg: ChatMessage = {
      id: Date.now().toString(),
      role: "player",
      text: playerText,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, playerMsg]);
    setInputValue("");

    try {
      const result = await onAction(selectedAction, playerText);
      const availableActions = result?.available_actions?.length
        ? `\n\nAvailable actions: ${result.available_actions.join(", ")}`
        : "";
      const narratorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "narrator",
        text: `${result?.narrative || "The dungeon echoes with your action..."}${availableActions}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, narratorMsg]);
    } catch (error) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: "narrator",
        text: `Error: ${error}. The dungeon remains silent...`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  return (
    <div className="game-board">
      <div className="board-header">
        <h2>Game Board</h2>
        <div className="board-status">
          {loading && <span className="status-loading">Processing...</span>}
        </div>
      </div>

      <div className="chat-container" role="log" aria-live="polite">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.role}`}>
            <span className="role-badge">{msg.role === "narrator" ? "DM" : "PC"}</span>
            <p className="message-text">{msg.text}</p>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="action-form">
        <select
          value={selectedAction}
          onChange={(e) => setSelectedAction(e.target.value)}
          className="action-select"
          disabled={loading}
          aria-label="Action type"
        >
          <option value="combat">Combat</option>
          <option value="exploration">Explore</option>
          <option value="social">Social</option>
          <option value="inventory">Inventory</option>
          <option value="rest">Rest</option>
        </select>

        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Describe your action..."
          className="action-input"
          disabled={loading}
          aria-label="Action description"
        />

        <button type="submit" className="action-button" disabled={loading}>
          {loading ? "..." : "Go"}
        </button>
      </form>
    </div>
  );
}

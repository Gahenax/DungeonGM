import { useState } from "react";
import "./CharacterSheet.css";

interface Character {
  name: string;
  class: string;
  level: number;
  hp: number;
  maxHp: number;
  ac: number;
  attributes: {
    str: number;
    dex: number;
    con: number;
    int: number;
    wis: number;
    cha: number;
  };
}

const defaultCharacter: Character = {
  name: "Adventurer",
  class: "Fighter",
  level: 1,
  hp: 10,
  maxHp: 10,
  ac: 10,
  attributes: {
    str: 15,
    dex: 10,
    con: 14,
    int: 10,
    wis: 12,
    cha: 13,
  },
};

export function CharacterSheet() {
  const [character] = useState<Character>(defaultCharacter);
  const [isExpanded, setIsExpanded] = useState(false);

  const calculateModifier = (score: number) => Math.floor((score - 10) / 2);

  return (
    <div className={`character-sheet ${isExpanded ? "expanded" : "collapsed"}`}>
      <button
        className="sheet-header"
        onClick={() => setIsExpanded(!isExpanded)}
        aria-expanded={isExpanded}
        aria-controls="character-sheet-body"
      >
        <div className="header-main">
          <h3>{character.name}</h3>
          <span className="level-badge">Level {character.level}</span>
        </div>
        <div className="header-stats">
          <div className="stat-box">
            <span className="stat-label">HP</span>
            <span className="stat-value">
              {character.hp}/{character.maxHp}
            </span>
          </div>
          <div className="stat-box">
            <span className="stat-label">AC</span>
            <span className="stat-value">{character.ac}</span>
          </div>
        </div>
      </button>

      {isExpanded && (
        <div id="character-sheet-body" className="sheet-body">
          <div className="sheet-section">
            <h4>Attributes</h4>
            <div className="attributes-grid">
              {Object.entries(character.attributes).map(([name, score]) => (
                <div key={name} className="attribute">
                  <span className="attr-name">{name.toUpperCase()}</span>
                  <span className="attr-score">{score}</span>
                  <span className="attr-mod">({calculateModifier(score)})</span>
                </div>
              ))}
            </div>
          </div>

          <div className="sheet-section">
            <h4>Hit Points</h4>
            <div className="hp-bar">
              <div
                className="hp-fill"
                style={{
                  width: `${(character.hp / character.maxHp) * 100}%`,
                }}
              />
            </div>
            <p className="hp-text">
              {character.hp} / {character.maxHp}
            </p>
          </div>

          <div className="sheet-section">
            <h4>Class & Background</h4>
            <p className="class-text">{character.class}</p>
          </div>
        </div>
      )}
    </div>
  );
}

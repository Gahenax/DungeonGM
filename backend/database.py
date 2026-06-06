import json
import sqlite3
from typing import Any, Dict, Optional


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    def initialize(self):
        self.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=10.0,
        )
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA journal_mode=WAL;")
        self.connection.execute("PRAGMA synchronous=NORMAL;")
        self._create_tables()
        print(f"Database: {self.db_path}")

    def _create_tables(self):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS campaigns (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                current_chapter INTEGER DEFAULT 0,
                visited_rooms TEXT,
                current_room_id TEXT,
                seed TEXT DEFAULT 'campaign_1',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS characters (
                id TEXT PRIMARY KEY,
                campaign_id TEXT NOT NULL,
                name TEXT NOT NULL,
                class TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                hp_max INTEGER DEFAULT 10,
                hp_current INTEGER DEFAULT 10,
                ac INTEGER DEFAULT 10,
                str INTEGER DEFAULT 10,
                dex INTEGER DEFAULT 10,
                con INTEGER DEFAULT 10,
                int INTEGER DEFAULT 10,
                wis INTEGER DEFAULT 10,
                cha INTEGER DEFAULT 10,
                equipment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT NOT NULL,
                character_id TEXT,
                action_type TEXT NOT NULL,
                description TEXT,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rooms (
                id TEXT PRIMARY KEY,
                campaign_id TEXT NOT NULL,
                name TEXT NOT NULL,
                depth INTEGER DEFAULT 0,
                description TEXT,
                feature TEXT,
                encounter TEXT,
                clue TEXT,
                exits TEXT,
                source_room_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        self._ensure_column("campaigns", "current_room_id", "TEXT")
        self._ensure_column("campaigns", "seed", "TEXT DEFAULT 'campaign_1'")

        self.connection.commit()

    def _ensure_column(self, table: str, column: str, definition: str):
        cursor = self.connection.cursor()
        cursor.execute(f"PRAGMA table_info({table})")
        columns = {row["name"] for row in cursor.fetchall()}
        if column not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def close(self):
        if self.connection:
            self.connection.close()

    def get_campaign(self, campaign_id: Optional[str] = None) -> Dict:
        cursor = self.connection.cursor()
        if campaign_id:
            cursor.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
        else:
            cursor.execute("SELECT * FROM campaigns ORDER BY created_at DESC LIMIT 1")
        row = cursor.fetchone()
        if not row:
            return {}
        result = dict(row)
        if result.get("visited_rooms"):
            result["visited_rooms"] = json.loads(result["visited_rooms"])
        return result

    def ensure_default_campaign(self) -> Dict:
        campaign = self.get_campaign("campaign_1")
        if campaign:
            return campaign

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO campaigns
            (id, name, description, current_chapter, visited_rooms, seed)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "campaign_1",
                "The First Descent",
                "A procedural dungeon campaign generated at the table.",
                0,
                json.dumps([]),
                "campaign_1",
            ),
        )
        self.connection.commit()
        return self.get_campaign("campaign_1")

    def get_character(self, character_id: Optional[str] = None) -> Dict:
        cursor = self.connection.cursor()
        if character_id:
            cursor.execute("SELECT * FROM characters WHERE id = ?", (character_id,))
        else:
            cursor.execute("SELECT * FROM characters ORDER BY created_at DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            result = dict(row)
            if result.get("equipment"):
                result["equipment"] = json.loads(result["equipment"])
            return result
        return {}

    def ensure_default_character(self, campaign_id: str = "campaign_1") -> Dict:
        character = self.get_character("player_1")
        if character:
            return character

        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO characters
            (id, campaign_id, name, class, level, hp_max, hp_current, ac, str, dex, con, int, wis, cha, equipment)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "player_1",
                campaign_id,
                "Adventurer",
                "Fighter",
                1,
                10,
                10,
                12,
                15,
                10,
                14,
                10,
                12,
                13,
                json.dumps(["torch", "shortsword", "rations"]),
            ),
        )
        self.connection.commit()
        return self.get_character("player_1")

    def get_room(self, room_id: str) -> Dict:
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
        row = cursor.fetchone()
        return self._decode_room(row) if row else {}

    def get_current_room(self, campaign_id: str) -> Dict:
        campaign = self.get_campaign(campaign_id)
        current_room_id = campaign.get("current_room_id")
        if not current_room_id:
            return {}
        return self.get_room(current_room_id)

    def save_room(self, room: Dict[str, Any]) -> Dict:
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO rooms
            (id, campaign_id, name, depth, description, feature, encounter, clue, exits, source_room_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                room["id"],
                room["campaign_id"],
                room["name"],
                room.get("depth", 0),
                room.get("description"),
                room.get("feature"),
                json.dumps(room.get("encounter")) if room.get("encounter") else None,
                room.get("clue"),
                json.dumps(room.get("exits", [])),
                room.get("source_room_id"),
            ),
        )
        self.connection.commit()
        return self.get_room(room["id"])

    def set_current_room(self, campaign_id: str, room_id: str):
        campaign = self.get_campaign(campaign_id)
        visited_rooms = campaign.get("visited_rooms") or []
        if room_id not in visited_rooms:
            visited_rooms.append(room_id)

        cursor = self.connection.cursor()
        cursor.execute(
            """
            UPDATE campaigns
            SET current_room_id = ?, visited_rooms = ?
            WHERE id = ?
            """,
            (room_id, json.dumps(visited_rooms), campaign_id),
        )
        self.connection.commit()

    def log_action(self, campaign_id: str, action_data: Dict):
        cursor = self.connection.cursor()
        cursor.execute(
            """
            INSERT INTO actions
            (campaign_id, character_id, action_type, description, result)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                campaign_id,
                action_data.get("character_id"),
                action_data.get("action_type"),
                action_data.get("description"),
                action_data.get("result", ""),
            ),
        )
        self.connection.commit()

    def reset(self):
        cursor = self.connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS rooms")
        cursor.execute("DROP TABLE IF EXISTS actions")
        cursor.execute("DROP TABLE IF EXISTS characters")
        cursor.execute("DROP TABLE IF EXISTS campaigns")
        self.connection.commit()
        self._create_tables()

    def _decode_room(self, row) -> Dict:
        result = dict(row)
        result["encounter"] = json.loads(result["encounter"]) if result.get("encounter") else None
        result["exits"] = json.loads(result["exits"]) if result.get("exits") else []
        return result

import json
import re
import aiosqlite
from typing import Any, Dict, Optional


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self._schema_cache = {}

    async def initialize(self):
        self.connection = await aiosqlite.connect(
            self.db_path,
            timeout=10.0,
        )
        self.connection.row_factory = aiosqlite.Row
        await self.connection.execute("PRAGMA journal_mode=WAL;")
        await self.connection.execute("PRAGMA synchronous=NORMAL;")
        await self._create_tables()
        print(f"Database: {self.db_path}")

    async def _create_tables(self):
        cursor = await self.connection.cursor()

        await cursor.execute(
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

        await cursor.execute(
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

        await cursor.execute(
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

        await cursor.execute(
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

        await self._ensure_column("campaigns", "current_room_id", "TEXT")
        await self._ensure_column("campaigns", "seed", "TEXT DEFAULT 'campaign_1'")

        # ⚡ Bolt: Add indexes on created_at for frequently queried tables
        # Prevent O(n) full table scans when fetching the most recent entries
        await cursor.execute("CREATE INDEX IF NOT EXISTS idx_campaigns_created_at ON campaigns(created_at)")
        await cursor.execute("CREATE INDEX IF NOT EXISTS idx_characters_created_at ON characters(created_at)")

        await self.connection.commit()

    async def _ensure_column(self, table: str, column: str, definition: str):
        if not re.match(r"^[a-zA-Z0-9_]+$", table):
            raise ValueError(f"Invalid table name: {table}")
        if not re.match(r"^[a-zA-Z0-9_]+$", column):
            raise ValueError(f"Invalid column name: {column}")
        if not re.match(r"^[a-zA-Z0-9_ '(),.\-]+$", definition):
            raise ValueError(f"Invalid column definition: {definition}")

        if table not in self._schema_cache:
            cursor = await self.connection.cursor()
            await cursor.execute("SELECT name FROM pragma_table_info(?)", (table,))
            self._schema_cache[table] = {row["name"] for row in await cursor.fetchall()}

        columns = self._schema_cache[table]
        if column not in columns:
            cursor = await self.connection.cursor()
            await cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            columns.add(column)

    async def close(self):
        if self.connection:
            await self.connection.close()

    async def get_campaign(self, campaign_id: Optional[str] = None) -> Dict:
        cursor = await self.connection.cursor()
        if campaign_id:
            await cursor.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
        else:
            await cursor.execute("SELECT * FROM campaigns ORDER BY created_at DESC LIMIT 1")
        row = await cursor.fetchone()
        if not row:
            return {}
        result = dict(row)
        if result.get("visited_rooms"):
            result["visited_rooms"] = json.loads(result["visited_rooms"])
        return result

    async def ensure_default_campaign(self) -> Dict:
        campaign = await self.get_campaign("campaign_1")
        if campaign:
            return campaign

        cursor = await self.connection.cursor()
        await cursor.execute(
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
        await self.connection.commit()
        return await self.get_campaign("campaign_1")

    async def get_character(self, character_id: Optional[str] = None) -> Dict:
        cursor = await self.connection.cursor()
        if character_id:
            await cursor.execute("SELECT * FROM characters WHERE id = ?", (character_id,))
        else:
            await cursor.execute("SELECT * FROM characters ORDER BY created_at DESC LIMIT 1")
        row = await cursor.fetchone()
        if row:
            result = dict(row)
            if result.get("equipment"):
                result["equipment"] = json.loads(result["equipment"])
            return result
        return {}

    async def ensure_default_character(self, campaign_id: str = "campaign_1") -> Dict:
        character = await self.get_character("player_1")
        if character:
            return character

        cursor = await self.connection.cursor()
        await cursor.execute(
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
        await self.connection.commit()
        return await self.get_character("player_1")

    async def get_room(self, room_id: str) -> Dict:
        cursor = await self.connection.cursor()
        await cursor.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
        row = await cursor.fetchone()
        return self._decode_room(row) if row else {}

    async def get_current_room(self, campaign_id: str) -> Dict:
        campaign = await self.get_campaign(campaign_id)
        current_room_id = campaign.get("current_room_id")
        if not current_room_id:
            return {}
        return await self.get_room(current_room_id)

    async def save_room(self, room: Dict[str, Any]) -> Dict:
        cursor = await self.connection.cursor()
        await cursor.execute(
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
        await self.connection.commit()
        return await self.get_room(room["id"])

    async def set_current_room(self, campaign_id: str, room_id: str):
        campaign = await self.get_campaign(campaign_id)
        visited_rooms = campaign.get("visited_rooms") or []
        if room_id not in visited_rooms:
            visited_rooms.append(room_id)

        cursor = await self.connection.cursor()
        await cursor.execute(
            """
            UPDATE campaigns
            SET current_room_id = ?, visited_rooms = ?
            WHERE id = ?
            """,
            (room_id, json.dumps(visited_rooms), campaign_id),
        )
        await self.connection.commit()

    async def log_action(self, campaign_id: str, action_data: Dict):
        cursor = await self.connection.cursor()
        await cursor.execute(
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
        await self.connection.commit()

    async def reset(self):
        cursor = await self.connection.cursor()
        await cursor.execute("DROP TABLE IF EXISTS rooms")
        await cursor.execute("DROP TABLE IF EXISTS actions")
        await cursor.execute("DROP TABLE IF EXISTS characters")
        await cursor.execute("DROP TABLE IF EXISTS campaigns")
        await self.connection.commit()
        self._schema_cache.clear()
        await self._create_tables()

    def _decode_room(self, row) -> Dict:
        result = dict(row)
        result["encounter"] = json.loads(result["encounter"]) if result.get("encounter") else None
        result["exits"] = json.loads(result["exits"]) if result.get("exits") else []
        return result

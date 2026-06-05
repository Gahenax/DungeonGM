import sqlite3
from typing import Optional, Dict, Any
import json

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
    
    def initialize(self):
        self.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=10.0
        )
        self.connection.row_factory = sqlite3.Row
        self.connection.execute('PRAGMA journal_mode=WAL;')
        self.connection.execute('PRAGMA synchronous=NORMAL;')
        self._create_tables()
        print(f"✅ Database: {self.db_path}")
    
    def _create_tables(self):
        cursor = self.connection.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                current_chapter INTEGER DEFAULT 0,
                visited_rooms TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
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
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id TEXT NOT NULL,
                character_id TEXT,
                action_type TEXT NOT NULL,
                description TEXT,
                result TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.connection.commit()
    
    def close(self):
        if self.connection:
            self.connection.close()
    
    def get_campaign(self, campaign_id: Optional[str] = None) -> Dict:
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM campaigns ORDER BY created_at DESC LIMIT 1')
        row = cursor.fetchone()
        return dict(row) if row else {}
    
    def get_character(self, character_id: Optional[str] = None) -> Dict:
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM characters ORDER BY created_at DESC LIMIT 1')
        row = cursor.fetchone()
        if row:
            result = dict(row)
            if result.get('equipment'):
                result['equipment'] = json.loads(result['equipment'])
            return result
        return {}
    
    def log_action(self, campaign_id: str, action_data: Dict):
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO actions 
            (campaign_id, character_id, action_type, description, result)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            campaign_id,
            action_data.get('character_id'),
            action_data.get('action_type'),
            action_data.get('description'),
            action_data.get('result', '')
        ))
        self.connection.commit()
    
    def reset(self):
        cursor = self.connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS actions')
        cursor.execute('DROP TABLE IF EXISTS characters')
        cursor.execute('DROP TABLE IF EXISTS campaigns')
        self.connection.commit()
        self._create_tables()

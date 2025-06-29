"""
Database layer for persistent conversation storage.
"""

import sqlite3
import json
import time
from typing import Optional, Dict, Any
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class ConversationDatabase:
    """SQLite-based conversation storage."""
    
    def __init__(self, db_path: str = "conversations.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database schema."""
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_updated 
                ON conversations(updated_at)
            """)
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper error handling."""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def save_conversation(self, conversation_id: str, data: Dict[str, Any]):
        """Save conversation data."""
        try:
            with self.get_connection() as conn:
                now = time.time()
                conn.execute("""
                    INSERT OR REPLACE INTO conversations 
                    (id, data, created_at, updated_at) 
                    VALUES (?, ?, COALESCE((SELECT created_at FROM conversations WHERE id = ?), ?), ?)
                """, (conversation_id, json.dumps(data), conversation_id, now, now))
                
        except Exception as e:
            logger.error(f"Failed to save conversation {conversation_id}: {e}")
            raise
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation data."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT data FROM conversations WHERE id = ?", 
                    (conversation_id,)
                )
                row = cursor.fetchone()
                
                if row:
                    return json.loads(row['data'])
                return None
                
        except Exception as e:
            logger.error(f"Failed to get conversation {conversation_id}: {e}")
            return None
    
    def cleanup_old_conversations(self, max_age_hours: int = 24):
        """Clean up old conversations."""
        try:
            cutoff_time = time.time() - (max_age_hours * 3600)
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "DELETE FROM conversations WHERE updated_at < ?", 
                    (cutoff_time,)
                )
                deleted_count = cursor.rowcount
                logger.info(f"Cleaned up {deleted_count} old conversations")
                
        except Exception as e:
            logger.error(f"Failed to cleanup conversations: {e}")

# Global database instance
db = ConversationDatabase()
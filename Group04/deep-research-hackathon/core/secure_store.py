import sqlite3
import json
import os
import time
from typing import Optional, Dict
from cryptography.fernet import Fernet
import streamlit as st

class SecureStore:
    """
    Encrypted persistence API.
    Uses a local SQLite DB to store encrypted blobs.
    The encryption key should ideally be rotated/managed securely.
    For this implementation, we generate/load a server-side key.
    """
    
    DB_PATH = "sessions.db"
    KEY_PATH = "server.key"

    def __init__(self):
        self._init_db()
        self.fernet = self._load_or_create_key()

    def _init_db(self):
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                payload BLOB,
                created_at REAL,
                expires_at REAL
            )
        ''')
        conn.commit()
        conn.close()

    def _load_or_create_key(self) -> Fernet:
        if os.path.exists(self.KEY_PATH):
            with open(self.KEY_PATH, "rb") as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.KEY_PATH, "wb") as f:
                f.write(key)
        return Fernet(key)

    def save_session(self, session_id: str, data: Dict[str, str], ttl_seconds: int = 86400):
        """Encrypts and saves data to SQLite."""
        json_bytes = json.dumps(data).encode('utf-8')
        encrypted = self.fernet.encrypt(json_bytes)
        
        now = time.time()
        expires = now + ttl_seconds
        
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO sessions (session_id, payload, created_at, expires_at)
            VALUES (?, ?, ?, ?)
        ''', (session_id, encrypted, now, expires))
        conn.commit()
        conn.close()

    def load_session(self, session_id: str) -> Optional[Dict[str, str]]:
        """Loads and decrypts data. Returns None if expired or missing."""
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        c.execute("SELECT payload, expires_at FROM sessions WHERE session_id = ?", (session_id,))
        row = c.fetchone()
        conn.close()

        if not row:
            return None
        
        payload, expires_at = row
        if time.time() > expires_at:
            self.delete_session(session_id) # Cleanup
            return None

        try:
            decrypted = self.fernet.decrypt(payload)
            return json.loads(decrypted.decode('utf-8'))
        except Exception as e:
            print(f"Decryption failed: {e}")
            return None

    def delete_session(self, session_id: str):
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()

    def cleanup_expired(self):
        """Removes all expired sessions."""
        conn = sqlite3.connect(self.DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM sessions WHERE expires_at < ?", (time.time(),))
        conn.commit()
        conn.close()

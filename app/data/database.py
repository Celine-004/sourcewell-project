"""
User Management and Session Persistence
"""
import sqlite3
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List


class UserDatabase:
    """SQLite-based user management and session persistence"""

    def __init__(self):
        db_path = Path(__file__).parent.parent.parent / '.data' / 'sourcewell.db'
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = str(db_path)
        self._initialize_tables()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize_tables(self):
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                patient_data TEXT,
                risk_results TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)

        conn.commit()
        conn.close()

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def create_user(self, username: str, password: str) -> bool:
        try:
            conn = self._get_connection()
            conn.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, self._hash_password(password))
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False

    def authenticate(self, username: str, password: str) -> Optional[int]:
        conn = self._get_connection()
        row = conn.execute(
            "SELECT id FROM users WHERE username = ? AND password_hash = ?",
            (username, self._hash_password(password))
        ).fetchone()
        conn.close()
        return row['id'] if row else None

    def create_session(self, user_id: int) -> int:
        conn = self._get_connection()
        cursor = conn.execute(
            "INSERT INTO sessions (user_id) VALUES (?)",
            (user_id,)
        )
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return session_id

    def save_patient_data(self, session_id: int, patient_data: Dict):
        conn = self._get_connection()
        conn.execute(
            "UPDATE sessions SET patient_data = ?, updated_at = ? WHERE id = ?",
            (json.dumps(patient_data), datetime.now(), session_id)
        )
        conn.commit()
        conn.close()

    def save_risk_results(self, session_id: int, risk_results: Dict):
        """Save serializable risk results"""
        conn = self._get_connection()
        conn.execute(
            "UPDATE sessions SET risk_results = ?, updated_at = ? WHERE id = ?",
            (json.dumps(risk_results, default=str), datetime.now(), session_id)
        )
        conn.commit()
        conn.close()

    def save_chat_message(self, session_id: int, role: str, content: str):
        conn = self._get_connection()
        conn.execute(
            "INSERT INTO chat_history (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        conn.commit()
        conn.close()

    def get_chat_history(self, session_id: int) -> List[Dict]:
        conn = self._get_connection()
        rows = conn.execute(
            "SELECT role, content, created_at FROM chat_history WHERE session_id = ? ORDER BY created_at",
            (session_id,)
        ).fetchall()
        conn.close()
        return [{"role": r['role'], "content": r['content'], "created_at": r['created_at']} for r in rows]

    def get_user_sessions(self, user_id: int) -> List[Dict]:
        conn = self._get_connection()
        rows = conn.execute(
            "SELECT id, created_at, updated_at, patient_data FROM sessions WHERE user_id = ? ORDER BY updated_at DESC",
            (user_id,)
        ).fetchall()
        conn.close()
        return [{"id": r['id'], "created_at": r['created_at'], "updated_at": r['updated_at'],
                 "patient_data": json.loads(r['patient_data']) if r['patient_data'] else None} for r in rows]

    def get_session(self, session_id: int) -> Optional[Dict]:
        conn = self._get_connection()
        row = conn.execute(
            "SELECT * FROM sessions WHERE id = ?",
            (session_id,)
        ).fetchone()
        conn.close()
        if row:
            return {
                "id": row['id'],
                "user_id": row['user_id'],
                "patient_data": json.loads(row['patient_data']) if row['patient_data'] else None,
                "risk_results": json.loads(row['risk_results']) if row['risk_results'] else None,
                "created_at": row['created_at'],
                "updated_at": row['updated_at']
            }
        return None

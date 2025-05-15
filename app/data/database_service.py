import sqlite3
import threading

class DatabaseService:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._lock = threading.Lock()
        self._init_schema()

    def _init_schema(self):
        with self.conn:
            self.conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                timestamp REAL,
                message TEXT
            )
            """)

    def store(self, records: list[dict], source: str):
        """
        Insère en batch les logs fournis.
        """
        with self._lock, self.conn:
            self.conn.executemany(
                "INSERT INTO logs(source, timestamp, message) VALUES (?, ?, ?)",
                [(source, rec["timestamp"], rec["message"]) for rec in records]
            )
import sqlite3
import os

class Database:
    def __init__(self, db_path="news_bot.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url_hash TEXT UNIQUE,
                    title TEXT,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def is_news_processed(self, url_hash):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT 1 FROM processed_news WHERE url_hash = ?", (url_hash,))
            return cursor.fetchone() is not None

    def mark_news_as_processed(self, url_hash, title):
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT INTO processed_news (url_hash, title) VALUES (?, ?)", (url_hash, title))
                conn.commit()
        except sqlite3.IntegrityError:
            pass # Already exists

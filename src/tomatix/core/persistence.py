# src/tomatix/core/persistence.py
import sqlite3

class PersistenceManager:
    """
    Handles reading/writing Focus Round-related data to a local SQLite database.
    We keep DB logic here so the rest of the app doesn’t worry about SQL details.
    """
    def __init__(self, db_path="focus_round_stats.db"):
        self.db_conn = sqlite3.connect(db_path)
        self._initialize_db()

    def _initialize_db(self):
        """
        Create tables for settings and stats if they don't exist.
        This ensures a minimal schema is always in place.
        """
        with self.db_conn:
            self.db_conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY,
                    focus_round_duration INTEGER,
                    recharge INTEGER,
                    big_recharge INTEGER
                )
            """)
            self.db_conn.execute("""
                CREATE TABLE IF NOT EXISTS focus_round_stats (
                    id INTEGER PRIMARY KEY,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    duration_minutes INTEGER DEFAULT 0
                )
            """)

    def save_settings(self, focus_round, recharge, big_recharge):
        with self.db_conn:
            self.db_conn.execute("""
                INSERT OR REPLACE INTO settings (id, focus_round_duration, recharge, big_recharge)
                VALUES (1, ?, ?, ?)
            """, (focus_round, recharge, big_recharge))

    def load_settings(self):
        cursor = self.db_conn.execute("""
            SELECT focus_round_duration, recharge, big_recharge FROM settings WHERE id = 1
        """)
        return cursor.fetchone()

    def log_focus_round(self, duration_minutes):
        """
        Inserts a new Focus Round record. duration_minutes can be the full or
        partial duration if the user skipped early.
        """
        with self.db_conn:
            self.db_conn.execute("""
                INSERT INTO focus_round_stats (duration_minutes) VALUES (?)
            """, (duration_minutes,))

    def get_statistics(self):
        """
        Returns a list of daily aggregates (date, focus_round_count, total_minutes).
        Useful for displaying stats in the UI.
        """
        cursor = self.db_conn.execute("""
            SELECT DATE(timestamp) as day,
                   COUNT(*) as focus_round_count,
                   SUM(duration_minutes) as total_minutes
            FROM focus_round_stats
            GROUP BY DATE(timestamp)
            ORDER BY day DESC
        """)
        return cursor.fetchall()

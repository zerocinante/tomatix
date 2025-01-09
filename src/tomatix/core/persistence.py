# src/tomatix/core/persistence.py
import sqlite3
from datetime import datetime
from tzlocal import get_localzone

class PersistenceManager:
    """
    Handles reading/writing Focus Round-related data to a local SQLite database.
    We keep DB logic here so the rest of the app doesn’t worry about SQL details.
    """
    def __init__(self, db_path="tomatix_stats.db"):
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
                    date DATE PRIMARY KEY,
                    total_focus_rounds INTEGER DEFAULT 0,
                    total_minutes INTEGER DEFAULT 0
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

    def get_local_date(self):
        local_zone = get_localzone()
        local_time = datetime.now(local_zone)
        return local_time.strftime("%Y-%m-%d")

    def log_focus_round(self, duration_minutes):
        """
        Log the completion of a Focus Round for the current day.
        Updates the daily stats or creates a new entry if none exists.
        """
        today = self.get_local_date()
        with self.db_conn:
            # Update if the row for today exists, otherwise insert a new row
            self.db_conn.execute("""
                INSERT INTO focus_round_stats (date, total_focus_rounds, total_minutes)
                VALUES (?, 1, ?)
                ON CONFLICT(date) DO UPDATE
                SET total_focus_rounds = total_focus_rounds + 1,
                    total_minutes = total_minutes + ?
            """, (today, duration_minutes, duration_minutes))

    def get_today_stats(self):
        """
        Fetch stats for the current day.
        Returns a tuple: (total_focus_rounds, total_minutes).
        """
        today = self.get_local_date()
        cursor = self.db_conn.execute("""
            SELECT total_focus_rounds, total_minutes
            FROM focus_round_stats
            WHERE date = ?
        """,(today,))
        result = cursor.fetchone()
        return result or (0, 0)  # Return (0, 0) if no entry exists for today

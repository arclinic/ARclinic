import os
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional


class MetricsDB:
    def __init__(self, db_path: str = "./data/metrics.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    account_type TEXT NOT NULL,
                    account_key TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    username TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)
            conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_snapshot_unique
                ON snapshots(date, account_type, account_key, platform, username)
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS posts_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    post_id TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    username TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    fetched_at TEXT DEFAULT (datetime('now')),
                    UNIQUE(post_id, platform, username)
                )
            """)
            conn.commit()

    def save_snapshot(self, date: str, account_type: str, account_key: str,
                      platform: str, username: str, data: Dict):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO snapshots
                (date, account_type, account_key, platform, username, data_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (date, account_type, account_key, platform, username, json.dumps(data, ensure_ascii=False)),
            )
            conn.commit()

    def get_previous_snapshot(self, account_type: str, account_key: str,
                              platform: str, username: str) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT data_json FROM snapshots
                WHERE account_type = ? AND account_key = ? AND platform = ? AND username = ?
                  AND date < date('now')
                ORDER BY date DESC LIMIT 1
                """,
                (account_type, account_key, platform, username),
            )
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
        return None

    def cache_posts(self, posts: List[Dict]):
        with sqlite3.connect(self.db_path) as conn:
            for p in posts:
                pid = p.get("post_id", "")
                platform = p.get("platform", "")
                username = p.get("username", "")
                if not pid:
                    continue
                conn.execute(
                    """
                    INSERT OR IGNORE INTO posts_cache (post_id, platform, username, data_json)
                    VALUES (?, ?, ?, ?)
                    """,
                    (str(pid), platform, username, json.dumps(p, ensure_ascii=False)),
                )
            conn.commit()

    def get_all_snapshots_for_period(self, account_type: str, months: int = 6) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                """
                SELECT date, account_key, platform, username, data_json
                FROM snapshots
                WHERE account_type = ?
                  AND date >= date('now', ?)
                ORDER BY date DESC
                """,
                (account_type, f"-{months} months"),
            )
            results = []
            for row in cursor.fetchall():
                d = json.loads(row[4])
                d["_date"] = row[0]
                d["_account_key"] = row[1]
                d["_platform"] = row[2]
                d["_username"] = row[3]
                results.append(d)
            return results

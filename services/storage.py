"""简单的 SQLite 存储，用于记录检测日志。"""
from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Iterable, List, Tuple

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT,
    text_sample TEXT,
    model_name TEXT,
    label INTEGER,
    proba REAL,
    success INTEGER,
    error TEXT,
    created_at TEXT
);
"""


class DetectionStorage:
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute(SCHEMA)
        conn.commit()
        conn.close()

    def add_record(
        self,
        url: str,
        text_sample: str,
        model_name: str,
        label: int,
        proba: float,
        success: bool = True,
        error: str | None = None,
    ) -> None:
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO detections(url, text_sample, model_name, label, proba, success, error, created_at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                url,
                text_sample[:200],
                model_name,
                label,
                proba,
                1 if success else 0,
                error,
                datetime.utcnow().isoformat(),
            ),
        )
        conn.commit()
        conn.close()

    def recent(self, limit: int = 50) -> List[Tuple]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute(
            "SELECT url, model_name, label, proba, success, error, created_at FROM detections"
            " ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()
        conn.close()
        return rows

    def export_all(self) -> List[Tuple]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.execute(
            "SELECT url, text_sample, model_name, label, proba, success, error, created_at FROM detections"
            " ORDER BY id DESC"
        )
        rows = cur.fetchall()
        conn.close()
        return rows

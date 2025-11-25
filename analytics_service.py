"""Analytics helpers for queue, detection quality, and throughput."""

from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from datetime import datetime
from typing import Dict, List


def _day(ts: str) -> str:
    return ts.split("T", 1)[0] if ts else ""


def daily_counts(conn: sqlite3.Connection) -> List[Dict[str, int]]:
    cursor = conn.execute(
        """
        SELECT date(updated_at) as day,
               COUNT(*) as total,
               SUM(CASE WHEN is_porn=1 THEN 1 ELSE 0 END) as hits
        FROM urls
        WHERE status='completed'
        GROUP BY day
        ORDER BY day DESC
        LIMIT 30
        """
    )
    data = []
    for row in cursor.fetchall():
        data.append({"day": row["day"], "total": row["total"], "hits": row["hits"]})
    return data


def status_breakdown(conn: sqlite3.Connection) -> Dict[str, int]:
    counts: Dict[str, int] = defaultdict(int)
    for row in conn.execute("SELECT status, COUNT(*) as c FROM urls GROUP BY status"):
        counts[row["status"]] = row["c"]
    return counts


def model_usage(conn: sqlite3.Connection) -> List[Dict[str, int]]:
    rows = conn.execute(
        """
        SELECT model, COUNT(*) as c, SUM(CASE WHEN is_porn=1 THEN 1 ELSE 0 END) as hits
        FROM urls
        WHERE status='completed'
        GROUP BY model
        ORDER BY c DESC
        LIMIT 20
        """
    ).fetchall()
    return [dict(row) for row in rows]


def top_domains(conn: sqlite3.Connection, limit: int = 20) -> List[Dict[str, int]]:
    cursor = conn.execute(
        """
        SELECT SUBSTR(url, 1, instr(SUBSTR(url, 9), '/')+8) as domain, COUNT(*) as c,
               SUM(CASE WHEN is_porn=1 THEN 1 ELSE 0 END) as hits
        FROM urls
        WHERE status='completed'
        GROUP BY domain
        ORDER BY c DESC
        LIMIT ?
        """,
        (limit,),
    )
    items = []
    for row in cursor.fetchall():
        items.append({"domain": row["domain"], "total": row["c"], "hits": row["hits"]})
    return items


def latency_buckets(conn: sqlite3.Connection) -> Dict[str, int]:
    buckets = {"<1s": 0, "1-5s": 0, "5-15s": 0, ">15s": 0}
    for row in conn.execute(
        """
        SELECT created_at, updated_at FROM urls WHERE status='completed'
        """
    ):
        start = datetime.fromisoformat(row["created_at"]).timestamp()
        end = datetime.fromisoformat(row["updated_at"]).timestamp()
        delta = end - start
        if delta < 1:
            buckets["<1s"] += 1
        elif delta < 5:
            buckets["1-5s"] += 1
        elif delta < 15:
            buckets["5-15s"] += 1
        else:
            buckets[">15s"] += 1
    return buckets


def export_events(conn: sqlite3.Connection, limit: int = 200) -> List[Dict[str, str]]:
    rows = conn.execute(
        """
        SELECT e.id, u.url, e.event, e.payload, e.created_at
        FROM events e
        LEFT JOIN urls u ON u.id = e.url_id
        ORDER BY e.id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [dict(row) for row in rows]


def log_event(conn: sqlite3.Connection, url_id: int, event: str, payload: Dict[str, str]) -> None:
    conn.execute(
        "INSERT INTO events(url_id, event, payload, created_at) VALUES(?, ?, ?, ?)",
        (url_id, event, json.dumps(payload), datetime.utcnow().isoformat()),
    )
    conn.commit()

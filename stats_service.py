import sqlite3
from typing import Dict, List

from analytics_service import daily_counts, latency_buckets, model_usage, status_breakdown, top_domains


def build_stats(conn: sqlite3.Connection) -> Dict[str, List[Dict[str, str]]]:
    return {
        "daily": daily_counts(conn),
        "models": model_usage(conn),
        "domains": top_domains(conn),
        "latency": latency_buckets(conn),
        "statuses": status_breakdown(conn),
    }

def build_stats(conn: sqlite3.Connection) -> Dict:
    return {
        "daily_counts": _daily_counts(conn),
        "model_usage": _model_usage(conn),
        "hit_rate": _hit_rate(conn),
    }


def _daily_counts(conn: sqlite3.Connection) -> List[Dict]:
    rows = conn.execute(
        """
        SELECT substr(created_at, 1, 10) AS day,
               COUNT(*) AS total,
               SUM(CASE WHEN is_porn=1 THEN 1 ELSE 0 END) AS hits
        FROM urls
        WHERE status='completed'
        GROUP BY day
        ORDER BY day ASC
        """
    ).fetchall()
    return [
        {
            "day": row["day"],
            "total": row["total"],
            "hits": row["hits"] or 0,
        }
        for row in rows
    ]


def _model_usage(conn: sqlite3.Connection) -> List[Dict]:
    rows = conn.execute(
        """
        SELECT model, COUNT(*) as total
        FROM urls
        WHERE status='completed'
        GROUP BY model
        ORDER BY total DESC
        """
    ).fetchall()
    return [{"model": row["model"], "total": row["total"]} for row in rows]


def _hit_rate(conn: sqlite3.Connection) -> float:
    row = conn.execute(
        "SELECT SUM(CASE WHEN is_porn=1 THEN 1 ELSE 0 END) as hits, COUNT(*) as total FROM urls WHERE status='completed'"
    ).fetchone()
    hits, total = row["hits"] or 0, row["total"] or 0
    return float(hits) / total if total else 0.0

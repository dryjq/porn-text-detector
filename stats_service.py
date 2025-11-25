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

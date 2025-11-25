import sqlite3
import threading
import time
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple

from database import init_db


KEYWORDS = ["porn", "xxx", "adult", "nsfw", "裸", "情色", "黄片"]


class DetectionService:
    def __init__(
        self,
        db_path: str,
        enable_workers: bool = True,
        seed_interval: float = 86400.0,
        seed_domains: Optional[List[str]] = None,
    ) -> None:
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        init_db(self.conn)
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.seed_interval = seed_interval
        if seed_domains:
            self.replace_seeds(seed_domains)
        self.worker_thread: Optional[threading.Thread] = None
        self.seed_thread: Optional[threading.Thread] = None
        if enable_workers:
            self.start_workers()

    def start_workers(self) -> None:
        if self.worker_thread and self.worker_thread.is_alive():
            return
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        self.seed_thread = threading.Thread(target=self._seed_loop, daemon=True)
        self.seed_thread.start()

    def stop_workers(self) -> None:
        self.stop_event.set()
        if self.worker_thread:
            self.worker_thread.join(timeout=2)
        if self.seed_thread:
            self.seed_thread.join(timeout=2)

    def enqueue_urls(self, urls: Iterable[str], model: str = "default") -> None:
        now = datetime.utcnow().isoformat()
        with self.lock:
            for url in urls:
                self.conn.execute(
                    """
                    INSERT INTO urls(url, status, model, created_at, updated_at)
                    VALUES(?, 'pending', ?, ?, ?)
                    """,
                    (url, model, now, now),
                )
            self.conn.commit()

    def progress(self) -> Dict[str, float]:
        with self.lock:
            rows = self.conn.execute("SELECT status, COUNT(*) as c FROM urls GROUP BY status").fetchall()
            counts = {row["status"]: row["c"] for row in rows}
            total = sum(counts.values())
            hits = self.conn.execute(
                "SELECT COUNT(*) FROM urls WHERE status='completed' AND is_porn=1"
            ).fetchone()[0]
        completed = counts.get("completed", 0)
        percent = float(completed) / total * 100 if total else 0.0
        return {
            "total": total,
            "pending": counts.get("pending", 0),
            "in_progress": counts.get("in_progress", 0),
            "completed": completed,
            "hit_rate": float(hits) / completed if completed else 0.0,
            "hits": hits,
            "percent": percent,
        }

    def recent_results(self, limit: int = 50) -> List[Dict[str, str]]:
        with self.lock:
            rows = self.conn.execute(
                "SELECT id, url, model, score, is_porn, status, updated_at FROM urls ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def replace_seeds(self, domains: List[str]) -> None:
        now = datetime.utcnow().isoformat()
        with self.lock:
            self.conn.execute("DELETE FROM seeds")
            for domain in domains:
                self.conn.execute(
                    "INSERT INTO seeds(domain, last_scanned_at, created_at) VALUES(?, ?, ?)",
                    (domain, None, now),
                )
            self.conn.commit()

    def list_seeds(self) -> List[str]:
        with self.lock:
            rows = self.conn.execute("SELECT domain FROM seeds ORDER BY domain").fetchall()
        return [row["domain"] for row in rows]

    def _worker_loop(self) -> None:
        while not self.stop_event.is_set():
            if not self.process_next_job():
                self.stop_event.wait(1)

    def process_next_job(self) -> bool:
        with self.lock:
            row = self.conn.execute(
                """
                SELECT id, url, model FROM urls
                WHERE status='pending'
                ORDER BY id
                LIMIT 1
                """
            ).fetchone()
            if not row:
                return False
            job_id, url, model = row["id"], row["url"], row["model"]
            now = datetime.utcnow().isoformat()
            self.conn.execute(
                "UPDATE urls SET status='in_progress', updated_at=? WHERE id=?",
                (now, job_id),
            )
            self.conn.commit()

        score, is_porn, message = simulate_detection(url, model)
        finished = datetime.utcnow().isoformat()
        with self.lock:
            self.conn.execute(
                """
                UPDATE urls SET status='completed', score=?, is_porn=?, message=?, updated_at=?
                WHERE id=?
                """,
                (score, 1 if is_porn else 0, message, finished, job_id),
            )
            self.conn.commit()
        return True

    def _seed_loop(self) -> None:
        while not self.stop_event.is_set():
            self._enqueue_seed_urls()
            self.stop_event.wait(self.seed_interval)

    def _enqueue_seed_urls(self) -> None:
        now_iso = datetime.utcnow().isoformat()
        with self.lock:
            seeds = self.conn.execute("SELECT domain FROM seeds").fetchall()
        for seed in seeds:
            domain = seed["domain"]
            generated_url = f"https://{domain}/content/{int(time.time())}"
            with self.lock:
                exists = self.conn.execute(
                    "SELECT 1 FROM urls WHERE url=? LIMIT 1", (generated_url,)
                ).fetchone()
                if exists:
                    continue
                self.conn.execute(
                    "INSERT INTO urls(url, status, model, created_at, updated_at) VALUES(?, 'pending', 'seed', ?, ?)",
                    (generated_url, now_iso, now_iso),
                )
                self.conn.execute(
                    "UPDATE seeds SET last_scanned_at=? WHERE domain=?",
                    (now_iso, domain),
                )
                self.conn.commit()


def simulate_detection(url: str, model: str) -> Tuple[float, bool, str]:
    lower = url.lower()
    score = 0.1
    for idx, keyword in enumerate(KEYWORDS):
        if keyword in lower:
            score = max(score, 0.6 + idx * 0.05)
    score = min(score, 0.99)
    is_porn = score >= 0.5
    message = "keyword hit" if is_porn else "safe"
    return score, is_porn, message

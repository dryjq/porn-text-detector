import random
import sqlite3
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple

from analytics_service import log_event
from database import init_db
from rules_library import explain_score, score_for_text


@dataclass
class Job:
    id: int
    url: str
    model: str
    priority: int
    attempts: int


class DetectionService:
    """Coordinates async detection, seeding, and progress tracking."""

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

    def enqueue_urls(self, urls: Iterable[str], model: str = "default", priority: int = 10) -> int:
        now = datetime.utcnow().isoformat()
        inserted = 0
        with self.lock:
            for url in urls:
                exists = self.conn.execute("SELECT 1 FROM urls WHERE url=?", (url,)).fetchone()
                if exists:
                    continue
                self.conn.execute(
                    """
                    INSERT INTO urls(url, status, model, priority, attempts, created_at, updated_at)
                    VALUES(?, 'pending', ?, ?, 0, ?, ?)
                    """,
                    (url, model, priority, now, now),
                )
                log_event(self.conn, self.conn.execute("SELECT last_insert_rowid()").fetchone()[0], "enqueued", {"model": model, "priority": priority})
                inserted += 1
            self.conn.commit()
        return inserted
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
            failed = counts.get("failed", 0)
        completed = counts.get("completed", 0)
        percent = float(completed) / total * 100 if total else 0.0
        return {
            "total": total,
            "pending": counts.get("pending", 0),
            "in_progress": counts.get("in_progress", 0),
            "completed": completed,
            "failed": failed,
            "hit_rate": float(hits) / completed if completed else 0.0,
            "hits": hits,
            "percent": percent,
        }

    def queue_status(self, limit: int = 100) -> List[Dict[str, str]]:
        with self.lock:
            rows = self.conn.execute(
                """
                SELECT id, url, status, model, priority, attempts, message, updated_at
                FROM urls
                ORDER BY status DESC, priority DESC, id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def recent_results(self, limit: int = 50) -> List[Dict[str, str]]:
        with self.lock:
            rows = self.conn.execute(
                """
                SELECT id, url, model, score, is_porn, status, priority, attempts, updated_at, message
                FROM urls
                WHERE status IN ('completed', 'failed')
                ORDER BY id DESC
                LIMIT ?
                """,
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

    def retry_failed(self) -> int:
        now = datetime.utcnow().isoformat()
        with self.lock:
            cur = self.conn.execute(
                "UPDATE urls SET status='pending', updated_at=?, message=NULL WHERE status='failed'",
                (now,),
            )
            self.conn.commit()
            return cur.rowcount

    def purge_completed(self, days: int = 30) -> int:
        cutoff = datetime.utcnow().timestamp() - days * 86400
        cutoff_iso = datetime.utcfromtimestamp(cutoff).isoformat()
        with self.lock:
            cur = self.conn.execute(
                "DELETE FROM urls WHERE status='completed' AND updated_at < ?",
                (cutoff_iso,),
            )
            self.conn.commit()
            return cur.rowcount

    def _worker_loop(self) -> None:
        while not self.stop_event.is_set():
            if not self.process_next_job():
                self.stop_event.wait(1)

    def _fetch_next_job(self) -> Optional[Job]:
        with self.lock:
            row = self.conn.execute(
                """
                SELECT id, url, model, priority, attempts FROM urls
                WHERE status='pending'
                ORDER BY priority DESC, id ASC
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
                return None
            now = datetime.utcnow().isoformat()
            self.conn.execute(
                "UPDATE urls SET status='in_progress', attempts=attempts+1, updated_at=? WHERE id=?",
                (now, row["id"]),
            )
            self.conn.commit()
            return Job(row["id"], row["url"], row["model"], row["priority"], row["attempts"])

    def process_next_job(self) -> bool:
        job = self._fetch_next_job()
        if not job:
            return False

        try:
            score, is_porn, message = simulate_detection(job.url, job.model)
            status = "completed"
        except Exception as exc:  # pragma: no cover - defensive branch
            score, is_porn = 0.0, False
            status = "failed"
            message = f"error: {exc}"

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
                UPDATE urls SET status=?, score=?, is_porn=?, message=?, updated_at=?
                WHERE id=?
                """,
                (status, score, 1 if is_porn else 0, message, finished, job.id),
            )
            self.conn.commit()
            log_event(self.conn, job.id, status, {"score": score, "is_porn": is_porn, "message": message})
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
                    """
                    INSERT INTO urls(url, status, model, priority, attempts, created_at, updated_at)
                    VALUES(?, 'pending', 'seed', 5, 0, ?, ?)
                    """,
                    "INSERT INTO urls(url, status, model, created_at, updated_at) VALUES(?, 'pending', 'seed', ?, ?)",
                    (generated_url, now_iso, now_iso),
                )
                self.conn.execute(
                    "UPDATE seeds SET last_scanned_at=? WHERE domain=?",
                    (now_iso, domain),
                )
                self.conn.commit()


def simulate_detection(url: str, model: str) -> Tuple[float, bool, str]:
    # Deterministic-ish pseudo model that uses keyword rules and URL entropy.
    lower = url.lower()
    data = score_for_text(lower)
    random.seed(hash((url, model)))
    jitter = random.random() * 0.15
    score = min(0.25 + data["max_weight"] + jitter + data["total_weight"] * 0.01, 0.99)
    is_porn = score >= 0.5
    message = explain_score(lower)
    if jitter > 0.1:
        message += "; boosted by anomaly detection"
    return round(score, 4), is_porn, message
    lower = url.lower()
    score = 0.1
    for idx, keyword in enumerate(KEYWORDS):
        if keyword in lower:
            score = max(score, 0.6 + idx * 0.05)
    score = min(score, 0.99)
    is_porn = score >= 0.5
    message = "keyword hit" if is_porn else "safe"
    return score, is_porn, message

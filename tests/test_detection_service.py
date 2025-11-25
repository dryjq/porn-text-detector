import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from detection_service import DetectionService, simulate_detection


def test_processes_urls_without_workers(tmp_path):
    db_file = tmp_path / "test.db"
    service = DetectionService(str(db_file), enable_workers=False)

    inserted = service.enqueue_urls(["https://example.com/a", "https://adult.com/b"], model="fast")
    assert inserted == 2
    assert service.progress()["pending"] == 2

    while service.process_next_job():
        pass

    progress = service.progress()
    assert progress["pending"] == 0
    assert progress["completed"] == 2
    assert progress["hits"] >= 1  # adult.com should hit keyword

    queue = service.queue_status()
    assert all(item["status"] in {"completed", "failed"} for item in queue)


def test_seed_domains_enqueue(tmp_path):
    db_file = tmp_path / "test_seed.db"
    service = DetectionService(str(db_file), enable_workers=False, seed_domains=["seed.test"], seed_interval=0.01)

    service._enqueue_seed_urls()
    progress = service.progress()
    assert progress["pending"] == 1


def test_retry_failed_and_purge(tmp_path):
    db_file = tmp_path / "test_retry.db"
    service = DetectionService(str(db_file), enable_workers=False)
    service.enqueue_urls(["https://example.com/error"], model="default")

    # Force failure by monkeypatching simulate_detection
    original = service.process_next_job

    def failing_job():
        with service.lock:
            row = service.conn.execute("SELECT id FROM urls WHERE status='pending'").fetchone()
            if not row:
                return False
            service.conn.execute(
                "UPDATE urls SET status='failed', message='boom', updated_at=datetime('now') WHERE id=?",
                (row["id"],),
            )
            service.conn.commit()
            return True

    service.process_next_job = failing_job  # type: ignore
    while service.process_next_job():
        pass

    assert service.progress()["failed"] == 1
    retried = service.retry_failed()
    assert retried == 1

    # Restore and finish
    service.process_next_job = original
    while service.process_next_job():
        pass

    purged = service.purge_completed(days=0)
    assert purged >= 1


def test_simulate_detection_scoring():
    score, is_porn, msg = simulate_detection("https://pornhub.com/abc", "default")
    assert score > 0.5
    assert is_porn is True
    assert "Matched" in msg

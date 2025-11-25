import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from detection_service import DetectionService


def test_processes_urls_without_workers(tmp_path):
    db_file = tmp_path / "test.db"
    service = DetectionService(str(db_file), enable_workers=False)

    service.enqueue_urls(["https://example.com/a", "https://adult.com/b"], model="fast")

    assert service.progress()["pending"] == 2

    while service.process_next_job():
        pass

    progress = service.progress()
    assert progress["pending"] == 0
    assert progress["completed"] == 2
    assert progress["hits"] >= 1  # adult.com should hit keyword


def test_seed_domains_enqueue(tmp_path):
    db_file = tmp_path / "test_seed.db"
    service = DetectionService(str(db_file), enable_workers=False, seed_domains=["seed.test"], seed_interval=0.01)

    # Manually trigger seed enqueue
    service._enqueue_seed_urls()
    progress = service.progress()
    assert progress["pending"] == 1

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from detection_service import DetectionService
from stats_service import build_stats


def test_stats_summary(tmp_path):
    db_file = tmp_path / "stats.db"
    service = DetectionService(str(db_file), enable_workers=False)

    service.enqueue_urls(["https://safe.com", "https://pornhub.com/video"], model="default")
    while service.process_next_job():
        pass

    stats = build_stats(service.conn)
    assert "daily" in stats and stats["daily"]
    assert any(item["hits"] >= 0 for item in stats["daily"])
    assert any(item["model"] == "default" for item in stats["models"])
    assert "latency" in stats
    assert "statuses" in stats
    assert stats["hit_rate"] >= 0
    assert any(item["hits"] >= 0 for item in stats["daily_counts"])
    assert any(item["model"] == "default" for item in stats["model_usage"])

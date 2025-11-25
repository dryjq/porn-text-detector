import os
from typing import Optional

from flask import Flask, jsonify, render_template, request

from detection_service import DetectionService
from stats_service import build_stats


def create_app(db_path: Optional[str] = None, enable_workers: bool = True) -> Flask:
    db_path = db_path or os.environ.get("APP_DB_PATH", "app.db")
    seed_interval = float(os.environ.get("SEED_SCAN_INTERVAL", "86400"))
    seeds = [s for s in os.environ.get("SEED_DOMAINS", "").split(",") if s]

    service = DetectionService(
        db_path=db_path,
        enable_workers=enable_workers,
        seed_interval=seed_interval,
        seed_domains=seeds,
    )

    app = Flask(__name__)
    app.config["DETECTION_SERVICE"] = service

    @app.teardown_appcontext
    def shutdown_session(exception=None):  # pragma: no cover - Flask hook
        # Threads stay alive for the lifetime of the process; only close DB when app stops.
        pass

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/stats")
    def stats_page():
        return render_template("stats.html")

    @app.route("/api/enqueue", methods=["POST"])
    def enqueue():
        payload = request.get_json(force=True)
        model = payload.get("model", "default")
        raw_urls = payload.get("urls", "")
        urls = [u.strip() for u in raw_urls.split("\n") if u.strip()]
        if not urls:
            return jsonify({"message": "No URLs provided"}), 400
        service.enqueue_urls(urls, model=model)
        return jsonify({"message": f"Queued {len(urls)} URLs", "count": len(urls)})

    @app.route("/api/progress")
    def progress():
        return jsonify(service.progress())

    @app.route("/api/results")
    def results():
        limit = int(request.args.get("limit", 50))
        return jsonify({"items": service.recent_results(limit=limit)})

    @app.route("/api/stats")
    def stats():
        return jsonify(build_stats(service.conn))

    @app.route("/api/seeds", methods=["GET", "POST"])
    def seeds_endpoint():
        if request.method == "POST":
            payload = request.get_json(force=True)
            domains = payload.get("domains", [])
            service.replace_seeds(domains)
            return jsonify({"message": "Seed domains updated", "count": len(domains)})
        return jsonify({"domains": service.list_seeds()})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)

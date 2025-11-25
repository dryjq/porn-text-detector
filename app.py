"""基于文本的色情网站识别教学系统入口。"""
from __future__ import annotations

import csv
import io
import os
from functools import wraps
from typing import List

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)

import config
from services.classify_service import ClassifyService

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY
service = ClassifyService()


# --------- 基础工具 ---------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user"):
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == config.LOGIN_USERNAME and password == config.LOGIN_PASSWORD:
            session["user"] = username
            return redirect(url_for("dashboard"))
        return render_template("login.html", error="账号或密码错误")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session.get("user"))


# --------- API 接口 ---------
@app.route("/api/classify-text", methods=["POST"])
@login_required
def api_classify_text():
    data = request.get_json() or {}
    text = data.get("text", "")
    model_name = data.get("model", "fasttext")
    if not text.strip():
        return jsonify({"error": "请输入文本内容"}), 400
    result = service.classify_single_text(text, model_name)
    return jsonify(result)


@app.route("/api/classify-urls", methods=["POST"])
@login_required
def api_classify_urls():
    model_name = request.form.get("model", "fasttext")
    url_text = request.form.get("urlText", "")
    urls: List[str] = []

    if url_text:
        urls.extend(url_text.splitlines())

    # 上传文件
    if "file" in request.files:
        file = request.files["file"]
        if file.filename:
            filename = file.filename
            ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
            if ext not in config.ALLOWED_EXTENSIONS:
                return jsonify({"error": "仅支持 txt 或 csv 文件"}), 400
            content = file.read().decode("utf-8", errors="ignore")
            urls.extend(content.splitlines())

    if not urls:
        return jsonify({"error": "请提供至少一个网址"}), 400

    results = service.classify_url_list(urls, model_name)
    return jsonify({"results": results})


@app.route("/api/history")
@login_required
def api_history():
    rows = service.get_history(limit=100)
    payload = [
        {
            "url": r[0],
            "model": r[1],
            "label": "色情" if r[2] == 1 else "正常",
            "proba": round(r[3], 3),
            "success": bool(r[4]),
            "error": r[5],
            "created_at": r[6],
        }
        for r in rows
    ]
    return jsonify(payload)


@app.route("/api/export")
@login_required
def api_export():
    rows = service.get_last_results() or []
    if not rows:
        return jsonify({"error": "没有可导出的结果"}), 400

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)
    mem = io.BytesIO()
    mem.write(output.getvalue().encode("utf-8"))
    mem.seek(0)
    return send_file(
        mem,
        mimetype="text/csv",
        as_attachment=True,
        download_name="detection_results.csv",
    )


@app.route("/api/export-history")
@login_required
def api_export_history():
    rows = service.export_history()
    if not rows:
        return jsonify({"error": "暂无历史记录"}), 400
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["URL", "文本摘要", "模型", "标签", "概率", "成功", "错误", "创建时间"])
    for row in rows:
        writer.writerow(row)
    mem = io.BytesIO()
    mem.write(output.getvalue().encode("utf-8"))
    mem.seek(0)
    return send_file(mem, mimetype="text/csv", as_attachment=True, download_name="history.csv")


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    app.run(debug=True)

"""模型管理与分类调用服务。"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

import config
from models.fasttext_model import FastTextClassifier
from models.textcnn_model import TextCNNClassifier
from models.roberta_small_model import RobertaSmallClassifier
from models.albert_model import AlbertClassifier
from services.url_fetcher import URLFetcher
from services.storage import DetectionStorage

logger = logging.getLogger(__name__)


class ModelManager:
    def __init__(self):
        self.models: Dict[str, object] = {}

    def get_model(self, model_name: str):
        model_name = model_name.lower()
        if model_name in self.models:
            return self.models[model_name]

        if model_name == "fasttext":
            model = FastTextClassifier(config.FASTTEXT_MODEL_PATH)
        elif model_name == "textcnn":
            model = TextCNNClassifier(config.TEXTCNN_MODEL_PATH)
        elif model_name == "roberta":
            model = RobertaSmallClassifier(config.ROBERTA_MODEL_PATH)
        elif model_name == "albert":
            model = AlbertClassifier(config.ALBERT_MODEL_PATH)
        else:
            raise ValueError(f"未知模型: {model_name}")
        self.models[model_name] = model
        return model


class ClassifyService:
    def __init__(self, model_manager: Optional[ModelManager] = None, storage: Optional[DetectionStorage] = None):
        self.model_manager = model_manager or ModelManager()
        self.storage = storage or DetectionStorage()
        self.fetcher = URLFetcher()
        self.last_results: List[dict] = []

    def classify_single_text(self, text: str, model_name: str) -> dict:
        model = self.model_manager.get_model(model_name)
        label = model.predict(text)
        proba = model.predict_proba(text)
        result = {
            "url": "单条文本",
            "label": "色情" if label == 1 else "正常",
            "proba": round(proba, 3),
            "model": model_name,
            "success": True,
        }
        self.storage.add_record("text", text, model_name, label, proba, success=True)
        self.last_results = [result]
        return result

    def classify_url(self, url: str, model_name: str) -> dict:
        fetched = self.fetcher.fetch(url)
        if not fetched.success:
            result = {
                "url": url,
                "label": "访问失败",
                "proba": 0.0,
                "model": model_name,
                "success": False,
                "error": fetched.error,
            }
            self.storage.add_record(url, fetched.text, model_name, 0, 0.0, success=False, error=fetched.error)
            return result

        model = self.model_manager.get_model(model_name)
        label = model.predict(fetched.text)
        proba = model.predict_proba(fetched.text)
        result = {
            "url": url,
            "label": "色情" if label == 1 else "正常",
            "proba": round(proba, 3),
            "model": model_name,
            "success": True,
        }
        self.storage.add_record(url, fetched.text, model_name, label, proba, success=True)
        return result

    def classify_url_list(self, urls: List[str], model_name: str) -> List[dict]:
        clean_urls = [u.strip() for u in urls if u.strip()]
        results = []
        for idx, url in enumerate(clean_urls, start=1):
            logger.info("[%s/%s] 检测 %s", idx, len(clean_urls), url)
            if not url.startswith("http"):
                url = "https://" + url
            results.append(self.classify_url(url, model_name))
        self.last_results = results
        return results

    def get_last_results(self) -> List[dict]:
        return self.last_results

    def get_history(self, limit: int = 50):
        return self.storage.recent(limit=limit)

    def export_history(self):
        return self.storage.export_all()

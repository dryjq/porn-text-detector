"""ALBERT 文本分类占位实现。"""
from typing import Tuple
import random

try:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer  # type: ignore
except Exception:  # noqa: BLE001
    AutoModelForSequenceClassification = None
    AutoTokenizer = None

from models import BaseTextClassifier


class AlbertClassifier(BaseTextClassifier):
    name = "albert"

    def __init__(self, model_path: str):
        super().__init__()
        self.model_path = model_path

    def load_model(self) -> None:
        if self.is_loaded:
            return
        if AutoModelForSequenceClassification and AutoTokenizer:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                self.model = AutoModelForSequenceClassification.from_pretrained(self.model_path)
            except Exception:
                self.model = None
        self.is_loaded = True

    def predict(self, text: str) -> int:
        label, _ = self._simple_rule(text)
        return label

    def predict_proba(self, text: str) -> float:
        _, prob = self._simple_rule(text)
        return min(1.0, prob + random.uniform(-0.08, 0.08))


def demo_predict(text: str) -> Tuple[int, float]:
    clf = AlbertClassifier(model_path="uer/albert-base-chinese")
    return clf.predict(text), clf.predict_proba(text)

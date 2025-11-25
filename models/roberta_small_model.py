"""RoBERTa-small 文本分类占位实现。

可使用 transformers 加载真实模型，这里使用规则模拟，避免启动时下载权重。
"""
from typing import Tuple
import random

try:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer  # type: ignore
except Exception:  # noqa: BLE001
    AutoModelForSequenceClassification = None
    AutoTokenizer = None

from models import BaseTextClassifier


class RobertaSmallClassifier(BaseTextClassifier):
    name = "roberta"

    def __init__(self, model_path: str):
        super().__init__()
        self.model_path = model_path
        self.tokenizer = None

    def load_model(self) -> None:
        if self.is_loaded:
            return
        if AutoModelForSequenceClassification and AutoTokenizer:
            # 为避免下载模型，这里只展示接口，实际部署时可启用
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
        return min(1.0, prob + random.uniform(-0.05, 0.05))


def demo_predict(text: str) -> Tuple[int, float]:
    clf = RobertaSmallClassifier(model_path="hfl/chinese-roberta-wwm-ext")
    return clf.predict(text), clf.predict_proba(text)

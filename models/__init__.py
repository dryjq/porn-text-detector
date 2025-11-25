"""模型基类与工厂方法。"""
import random
from abc import ABC, abstractmethod
from typing import Tuple


class BaseTextClassifier(ABC):
    """文本分类器统一接口。"""

    name: str = "base"

    def __init__(self):
        self.model = None
        self.is_loaded = False

    @abstractmethod
    def load_model(self) -> None:
        """加载模型权重或初始化占位模型。"""

    @abstractmethod
    def predict(self, text: str) -> int:
        """返回类别标签，1 表示色情，0 表示正常。"""

    @abstractmethod
    def predict_proba(self, text: str) -> float:
        """返回预测为色情的概率 (0~1)。"""

    def _simple_rule(self, text: str) -> Tuple[int, float]:
        """简单的关键词启发式模型，保证教学示例可运行。"""
        keywords = ["色情", "sex", "成人", "AV", "激情", "裸", "porn"]
        hit = sum(word.lower() in text.lower() for word in keywords)
        # 规则：命中越多，概率越高
        prob = min(1.0, 0.2 * hit + random.uniform(0, 0.15))
        label = 1 if prob >= 0.45 else 0
        return label, prob

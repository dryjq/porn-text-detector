"""fastText 分类模型封装。

教学演示使用关键词规则作为占位，若本地已有 fastText 模型可替换 load_model 实现。
"""
from typing import Tuple

try:
    import fasttext  # type: ignore
except Exception:  # noqa: BLE001
    fasttext = None

from models import BaseTextClassifier
import os


class FastTextClassifier(BaseTextClassifier):
    name = "fasttext"

    def __init__(self, model_path: str):
        super().__init__()
        self.model_path = model_path

    def load_model(self) -> None:
        if self.is_loaded:
            return
        if fasttext and os.path.exists(self.model_path):
            self.model = fasttext.load_model(self.model_path)
        else:
            # 占位模型：使用关键词规则
            self.model = None
        self.is_loaded = True

    def predict(self, text: str) -> int:
        self.load_model()
        if self.model:
            label = self.model.predict(text)[0][0]
            return 1 if "__label__1" in label else 0
        label, _ = self._simple_rule(text)
        return label

    def predict_proba(self, text: str) -> float:
        self.load_model()
        if self.model:
            _, prob = self.model.predict(text)
            return float(prob[0])
        _, prob = self._simple_rule(text)
        return prob

    @staticmethod
    def train_fasttext(training_file: str, model_path: str) -> str:
        """示例训练接口，便于教学。"""
        if not fasttext:
            raise ImportError("fasttext 库未安装，无法训练")
        model = fasttext.train_supervised(training_file, lr=0.5, epoch=5, wordNgrams=2)
        model.save_model(model_path)
        return model_path


def demo_predict(text: str) -> Tuple[int, float]:
    """方便脚本测试的辅助函数。"""
    clf = FastTextClassifier(model_path="/tmp/non-exist.bin")
    return clf.predict(text), clf.predict_proba(text)

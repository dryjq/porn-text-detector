"""项目配置文件，包含登录信息、模型路径等。"""
import os

# Flask 配置
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

# 登录账号配置（教学演示用）
LOGIN_USERNAME = os.environ.get("LOGIN_USERNAME", "admin")
LOGIN_PASSWORD = os.environ.get("LOGIN_PASSWORD", "123456")

# 数据库配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "detector_logs.db")

# 模型文件路径（如果替换为训练好的模型，可修改这里）
MODEL_DIR = os.path.join(BASE_DIR, "model_files")
FASTTEXT_MODEL_PATH = os.path.join(MODEL_DIR, "fasttext.bin")
TEXTCNN_MODEL_PATH = os.path.join(MODEL_DIR, "textcnn.pt")
ROBERTA_MODEL_PATH = os.path.join(MODEL_DIR, "roberta_small")
ALBERT_MODEL_PATH = os.path.join(MODEL_DIR, "albert")

# 请求相关配置
default_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}
REQUEST_TIMEOUT = 8

# 允许上传的文件类型
ALLOWED_EXTENSIONS = {"txt", "csv"}

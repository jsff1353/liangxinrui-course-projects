"""应用配置。

默认连接 MySQL；把 .env 中 USE_SQLITE 设为 1 可切换为 SQLite 演示模式，
方便在没有安装 MySQL 的电脑上直接运行与答辩演示。
"""
import os
import sys
from datetime import timedelta
from urllib.parse import quote_plus

from dotenv import load_dotenv

APP_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(APP_DIR)


def _load_env():
    """按优先级读取 .env：显式路径 > exe 同目录 > 打包资源 > backend 根目录。"""
    candidates = []
    explicit = os.environ.get("MUSIC_ENV_FILE")
    if explicit:
        candidates.append(explicit)
    if getattr(sys, "frozen", False):  # PyInstaller 打包后的运行环境
        candidates.append(os.path.join(os.path.dirname(sys.executable), ".env"))
        if hasattr(sys, "_MEIPASS"):
            candidates.append(os.path.join(sys._MEIPASS, ".env"))
    candidates.append(os.path.join(BACKEND_DIR, ".env"))
    for path in candidates:
        if path and os.path.isfile(path):
            load_dotenv(path, override=False)
            return path
    return None


ENV_FILE = _load_env()


def create_database_uri():
    """根据配置生成 SQLAlchemy 连接串。"""
    if os.getenv("USE_SQLITE", "0").strip().lower() in ("1", "true", "yes", "on"):
        db_path = os.getenv("SQLITE_PATH") or os.path.join(BACKEND_DIR, "music.db")
        return "sqlite:///" + db_path.replace("\\", "/")

    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "123456")
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME", "music_collection")
    return (
        f"mysql+pymysql://{quote_plus(user)}:{quote_plus(password)}"
        f"@{host}:{port}/{name}?charset=utf8mb4"
    )


DATABASE_URI = create_database_uri()


class Config:
    """Flask 全局配置。"""

    # 长度需 >= 32 字节，避免 PyJWT 的安全强度警告
    SECRET_KEY = os.getenv("SECRET_KEY", "music-collection-desktop-dev-secret-key-2026")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=int(os.getenv("TOKEN_EXPIRE_DAYS", "7")))

    SQLALCHEMY_DATABASE_URI = DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = (
        {} if DATABASE_URI.startswith("sqlite") else {"pool_pre_ping": True, "pool_recycle": 3600}
    )

    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 请求体上限 2MB

"""首次启动自动初始化：缺表则建表、确保管理员账号存在，并按需播种演示数据。

这样无论用 MySQL 还是 SQLite、无论是否手工执行过 schema.sql，
只要后端能连上数据库，启动后即可直接注册 / 登录，并看到一批可试听的示例收藏。
"""
import os

from sqlalchemy import inspect

from .demo_data import seed_demo_data
from .extensions import db
from .models import User

REQUIRED_TABLES = {"users", "playlists", "songs", "tags", "song_tags"}


def initialize(app, verbose=False, seed=True):
    """seed=False 用于命令行脚本自行控制播种时机（例如 --force）。"""
    with app.app_context():
        existing = set(inspect(db.engine).get_table_names())
        missing = REQUIRED_TABLES - existing
        if missing:
            db.create_all()  # checkfirst=True，不会破坏已有表
            if verbose:
                print(f"[init] 已自动创建数据表：{', '.join(sorted(missing))}")
        elif verbose:
            print("[init] 数据表已存在，跳过建表")

        username = (os.getenv("ADMIN_USERNAME") or "admin").strip()
        password = os.getenv("ADMIN_PASSWORD") or "admin123"
        admin = User.query.filter_by(username=username).first()
        if admin is None:
            admin = User(
                username=username,
                nickname="超级管理员",
                email="admin@music.local",
                role="admin",
                status=1,
            )
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            if verbose:
                print(f"[init] 管理员账号已创建：{username} / {password}")
        elif admin.role != "admin":
            admin.role = "admin"
            db.session.commit()

        if seed:
            # 幂等：管理员名下已有歌曲时自动跳过，不会覆盖用户自己的收藏。
            seed_demo_data(verbose=verbose)

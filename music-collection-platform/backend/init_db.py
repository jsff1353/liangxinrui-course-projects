"""显式初始化数据库：python init_db.py

说明：直接运行 python run.py 也会在首次启动时自动完成同样的初始化
（建表 + 创建管理员 + 播种演示数据）。
本脚本适合需要单独检查/初始化数据库的场景；演示数据由 SEED_DEMO_DATA 控制。
"""
from app import create_app
from app.bootstrap import initialize
from app.config import DATABASE_URI


def main():
    app = create_app()
    initialize(app, verbose=True)
    print(f"[OK] 数据库初始化完成 -> {DATABASE_URI}")


if __name__ == "__main__":
    main()

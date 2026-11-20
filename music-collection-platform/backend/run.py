"""后端启动入口：python run.py"""
import os

from app import create_app
from app.bootstrap import initialize
from app.config import DATABASE_URI

app = create_app()

# 首次启动自动建表 + 创建管理员（已存在则跳过，不会覆盖数据）
try:
    initialize(app, verbose=True)
except Exception as exc:
    print(f"[错误] 数据库初始化失败：{exc}")
    print("请检查 backend/.env 中 DB_* 配置、MySQL 服务状态，或先执行 database/schema.sql")
    raise SystemExit(1)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    print(f"[Music Collection] 数据库：{DATABASE_URI.split('@')[-1]}")
    print(f"[Music Collection] API 已启动: http://127.0.0.1:{port}/api")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

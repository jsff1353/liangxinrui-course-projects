"""Flask 应用工厂。"""
from flask import Flask

from .config import Config, DATABASE_URI
from .extensions import cors, db, jwt
from .utils import error, success
from .api import register_blueprints


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config.from_object(Config)
    app.json.ensure_ascii = False  # 中文响应不转义

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    register_blueprints(app)

    @app.get("/api/health")
    def health():
        """Electron 启动时用于探测后端是否就绪。"""
        try:
            db.session.execute(db.text("SELECT 1"))
            db_ready = True
        except Exception:
            db.session.rollback()
            db_ready = False
        return success(
            {
                "status": "running",
                "dbReady": db_ready,
                "database": "sqlite" if DATABASE_URI.startswith("sqlite") else "mysql",
            }
        )

    @app.errorhandler(404)
    def not_found(_):
        return error("接口不存在", 404, 404)

    @app.errorhandler(405)
    def method_not_allowed(_):
        return error("请求方法不被允许", 405, 405)

    @app.errorhandler(413)
    def too_large(_):
        return error("提交内容过大", 413, 413)

    @app.errorhandler(500)
    def internal_error(exc):
        db.session.rollback()
        app.logger.exception(exc)
        return error("服务器内部错误，请查看后端日志", 500, 500)

    @jwt.unauthorized_loader
    def missing_token(reason):
        return error("请先登录", 401, 401)

    @jwt.expired_token_loader
    def expired_token(header, payload):
        return error("登录已过期，请重新登录", 401, 401)

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return error("登录凭证无效，请重新登录", 401, 401)

    return app

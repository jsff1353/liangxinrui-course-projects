"""RESTful 接口蓝图注册。"""
from .admin import bp as admin_bp
from .auth import bp as auth_bp
from .playlists import bp as playlists_bp
from .songs import bp as songs_bp
from .tags import bp as tags_bp
from .users import bp as users_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(playlists_bp, url_prefix="/api/playlists")
    app.register_blueprint(songs_bp, url_prefix="/api/songs")
    app.register_blueprint(tags_bp, url_prefix="/api/tags")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

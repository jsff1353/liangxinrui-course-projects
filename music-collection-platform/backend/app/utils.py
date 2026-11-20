"""通用工具：统一响应、鉴权装饰器、参数处理、分页。"""
from functools import wraps

from flask import g, jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from .extensions import db
from .models import User


def success(data=None, message="操作成功", **extra):
    """成功响应：{ code: 0, message, data }"""
    payload = {"code": 0, "message": message, "data": data}
    payload.update(extra)
    return jsonify(payload)


def error(message="请求失败", code=1, http_status=400):
    """失败响应：HTTP 状态码与业务 code 同步，便于前端拦截器处理。"""
    return jsonify({"code": code, "message": message, "data": None}), http_status


def get_json_body():
    return request.get_json(silent=True) or {}


def text(data, key, default=""):
    """安全取字符串并去除首尾空格。"""
    value = data.get(key, default)
    return str(value).strip() if value is not None else ""


def current_user():
    uid = get_jwt_identity()
    try:
        uid = int(uid)
    except (TypeError, ValueError):
        return None
    return db.session.get(User, uid)


def login_required(fn):
    """校验 JWT + 账号状态，并把当前用户挂到 g.current_user。"""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user = current_user()
        if user is None:
            return error("登录状态无效，请重新登录", 401, 401)
        if user.status != 1:
            return error("账号已被管理员禁用", 403, 403)
        g.current_user = user
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    """管理员权限校验（内部已包含登录校验）。"""

    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if g.current_user.role != "admin":
            return error("需要管理员权限", 403, 403)
        return fn(*args, **kwargs)

    return wrapper


def paginate(query, serializer):
    """对 SQLAlchemy 查询做分页并序列化。"""
    page = max(1, request.args.get("page", 1, type=int) or 1)
    size = min(100, max(1, request.args.get("size", 20, type=int) or 20))
    result = query.paginate(page=page, per_page=size, error_out=False)
    return {
        "list": [serializer(item) for item in result.items],
        "total": result.total,
        "page": page,
        "size": size,
        "pages": result.pages,
    }


def owned(model, object_id, user_id):
    """取一条属于当前用户的记录；返回 (对象, 错误响应)。"""
    obj = db.session.get(model, object_id)
    if obj is None:
        return None, error("数据不存在或已被删除", 404, 404)
    if obj.user_id != user_id:
        return None, error("无权操作他人数据", 403, 403)
    return obj, None

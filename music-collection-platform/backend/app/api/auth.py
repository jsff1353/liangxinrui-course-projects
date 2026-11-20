"""用户认证：注册 / 登录。"""
import re

from flask import Blueprint
from flask_jwt_extended import create_access_token

from ..extensions import db
from ..models import User
from ..utils import error, get_json_body, success, text

bp = Blueprint("auth", __name__)
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,32}$")


@bp.post("/register")
def register():
    data = get_json_body()
    username = text(data, "username").lower()
    password = str(data.get("password") or "")

    if not USERNAME_RE.match(username):
        return error("用户名需为 3-32 位字母、数字或下划线")
    if not 6 <= len(password) <= 64:
        return error("密码长度需为 6-64 位")
    if User.query.filter_by(username=username).first():
        return error("该用户名已被注册")

    email = text(data, "email")
    if email and ("@" not in email or len(email) > 120):
        return error("邮箱格式不正确")

    user = User(
        username=username,
        nickname=(text(data, "nickname") or username)[:64],
        email=email[:120],
        role="user",
        status=1,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return success({"token": token, "user": user.to_dict()}, "注册成功")


@bp.post("/login")
def login():
    data = get_json_body()
    username = text(data, "username").lower()
    password = str(data.get("password") or "")

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return error("用户名或密码错误")
    if user.status != 1:
        return error("账号已被禁用，请联系管理员", 403, 403)

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return success({"token": token, "user": user.to_dict()}, "登录成功")

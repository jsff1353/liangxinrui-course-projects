"""用户模块：个人信息、密码修改、首页统计。"""
from flask import Blueprint, g

from ..extensions import db
from ..models import Playlist, Song, Tag
from ..utils import error, get_json_body, login_required, success, text

bp = Blueprint("users", __name__)


@bp.get("/me")
@login_required
def get_me():
    return success(g.current_user.to_dict())


@bp.put("/me")
@login_required
def update_me():
    data = get_json_body()
    user = g.current_user

    nickname = text(data, "nickname")
    if not nickname:
        return error("昵称不能为空")
    email = text(data, "email")
    if email and ("@" not in email or len(email) > 120):
        return error("邮箱格式不正确")

    user.nickname = nickname[:64]
    user.email = email[:120]
    user.avatar = text(data, "avatar")[:500]
    db.session.commit()
    return success(user.to_dict(), "个人资料已更新")


@bp.put("/password")
@login_required
def change_password():
    data = get_json_body()
    old = str(data.get("oldPassword") or "")
    new = str(data.get("newPassword") or "")
    user = g.current_user

    if not user.check_password(old):
        return error("原密码不正确")
    if not 6 <= len(new) <= 64:
        return error("新密码长度需为 6-64 位")
    user.set_password(new)
    db.session.commit()
    return success(None, "密码修改成功，请重新登录")


@bp.get("/stats")
@login_required
def stats():
    """首页概览数据。"""
    uid = g.current_user.id
    recent = (
        Song.query.filter_by(user_id=uid)
        .order_by(Song.created_at.desc(), Song.id.desc())
        .limit(6)
        .all()
    )
    return success(
        {
            "playlistCount": Playlist.query.filter_by(user_id=uid).count(),
            "songCount": Song.query.filter_by(user_id=uid).count(),
            "tagCount": Tag.query.filter_by(user_id=uid).count(),
            "recentSongs": [s.to_dict() for s in recent],
        }
    )

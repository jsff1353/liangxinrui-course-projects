"""管理员后台：数据总览、用户管理、违规内容删除。"""
from flask import Blueprint, g, request
from sqlalchemy import or_

from ..extensions import db
from ..models import Playlist, Song, Tag, User
from ..utils import admin_required, error, get_json_body, paginate, success

bp = Blueprint("admin", __name__)


@bp.get("/overview")
@admin_required
def overview():
    return success(
        {
            "userCount": User.query.count(),
            "playlistCount": Playlist.query.count(),
            "songCount": Song.query.count(),
            "tagCount": Tag.query.count(),
            "recentUsers": [
                u.to_dict()
                for u in User.query.order_by(User.created_at.desc(), User.id.desc()).limit(5).all()
            ],
        }
    )


@bp.get("/users")
@admin_required
def list_users():
    query = User.query
    kw = (request.args.get("kw") or "").strip()
    if kw:
        like = f"%{kw}%"
        query = query.filter(or_(User.username.like(like), User.nickname.like(like)))
    query = query.order_by(User.created_at.desc(), User.id.desc())
    return success(paginate(query, lambda u: u.to_dict()))


@bp.put("/users/<int:user_id>/status")
@admin_required
def set_user_status(user_id):
    if user_id == g.current_user.id:
        return error("不能禁用当前登录账号")
    target = db.session.get(User, user_id)
    if target is None:
        return error("用户不存在", 404, 404)
    data = get_json_body()
    status = 1 if data.get("status") in (1, "1", True) else 0
    target.status = status
    db.session.commit()
    return success(target.to_dict(), "账号状态已更新")


@bp.put("/users/<int:user_id>/role")
@admin_required
def set_user_role(user_id):
    target = db.session.get(User, user_id)
    if target is None:
        return error("用户不存在", 404, 404)
    data = get_json_body()
    role = "admin" if data.get("role") == "admin" else "user"
    if user_id == g.current_user.id and role != "admin":
        return error("不能取消自己的管理员权限")
    target.role = role
    db.session.commit()
    return success(target.to_dict(), "用户角色已更新")


@bp.delete("/users/<int:user_id>")
@admin_required
def delete_user(user_id):
    if user_id == g.current_user.id:
        return error("不能删除当前登录账号")
    target = db.session.get(User, user_id)
    if target is None:
        return error("用户不存在", 404, 404)
    if target.role == "admin" and User.query.filter_by(role="admin", status=1).count() <= 1:
        return error("至少保留一个启用状态的管理员账号")

    # 由 ORM 级联删除该用户的歌单 / 歌曲 / 标签及歌曲-标签关联行
    db.session.delete(target)
    db.session.commit()
    return success(None, "用户及其全部数据已删除")


@bp.get("/songs")
@admin_required
def list_all_songs():
    query = Song.query
    kw = (request.args.get("kw") or "").strip()
    if kw:
        like = f"%{kw}%"
        query = query.filter(or_(Song.title.like(like), Song.artist.like(like), Song.notes.like(like)))
    query = query.order_by(Song.created_at.desc(), Song.id.desc())

    def serialize(song):
        item = song.to_dict()
        item["owner"] = song.user.username if song.user else "-"
        return item

    return success(paginate(query, serialize))


@bp.delete("/songs/<int:song_id>")
@admin_required
def delete_any_song(song_id):
    song = db.session.get(Song, song_id)
    if song is None:
        return error("歌曲不存在", 404, 404)
    # Song.tags 关系会自动清理 song_tags 关联行，不可在此手动删除（会导致 StaleDataError）
    db.session.delete(song)
    db.session.commit()
    return success(None, "违规歌曲已删除")


@bp.get("/playlists")
@admin_required
def list_all_playlists():
    query = Playlist.query.order_by(Playlist.created_at.desc(), Playlist.id.desc())

    def serialize(playlist):
        item = playlist.to_dict()
        item["owner"] = playlist.user.username if playlist.user else "-"
        return item

    return success(paginate(query, serialize))


@bp.delete("/playlists/<int:playlist_id>")
@admin_required
def delete_any_playlist(playlist_id):
    playlist = db.session.get(Playlist, playlist_id)
    if playlist is None:
        return error("歌单不存在", 404, 404)
    Song.query.filter_by(playlist_id=playlist_id).update(
        {Song.playlist_id: None}, synchronize_session=False
    )
    db.session.delete(playlist)
    db.session.commit()
    return success(None, "违规歌单已删除")

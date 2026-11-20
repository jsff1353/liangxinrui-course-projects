"""歌单模块：增删改查。删除歌单不会删除歌曲，歌曲转为「未分类」。"""
from flask import Blueprint, g

from ..extensions import db
from ..models import Playlist, Song
from ..utils import error, get_json_body, login_required, owned, success, text

bp = Blueprint("playlists", __name__)


@bp.get("")
@login_required
def list_playlists():
    uid = g.current_user.id
    items = (
        Playlist.query.filter_by(user_id=uid)
        .order_by(Playlist.created_at.desc(), Playlist.id.desc())
        .all()
    )
    counts = dict(
        db.session.query(Song.playlist_id, db.func.count(Song.id))
        .filter(Song.user_id == uid, Song.playlist_id.isnot(None))
        .group_by(Song.playlist_id)
        .all()
    )
    return success([p.to_dict(counts.get(p.id, 0)) for p in items])


@bp.post("")
@login_required
def create_playlist():
    data = get_json_body()
    name = text(data, "name")
    if not name:
        return error("歌单名称不能为空")
    if len(name) > 100:
        return error("歌单名称不能超过 100 个字符")

    playlist = Playlist(
        user_id=g.current_user.id,
        name=name,
        description=text(data, "description")[:500],
        cover=text(data, "cover")[:500],
    )
    db.session.add(playlist)
    db.session.commit()
    return success(playlist.to_dict(0), "歌单创建成功")


@bp.get("/<int:playlist_id>")
@login_required
def get_playlist(playlist_id):
    playlist, err = owned(Playlist, playlist_id, g.current_user.id)
    if err:
        return err
    songs = (
        Song.query.filter_by(user_id=g.current_user.id, playlist_id=playlist_id)
        .order_by(Song.created_at.desc(), Song.id.desc())
        .all()
    )
    result = playlist.to_dict(len(songs))
    result["songs"] = [s.to_dict() for s in songs]
    return success(result)


@bp.put("/<int:playlist_id>")
@login_required
def update_playlist(playlist_id):
    playlist, err = owned(Playlist, playlist_id, g.current_user.id)
    if err:
        return err
    data = get_json_body()
    name = text(data, "name")
    if not name:
        return error("歌单名称不能为空")

    playlist.name = name[:100]
    playlist.description = text(data, "description")[:500]
    playlist.cover = text(data, "cover")[:500]
    db.session.commit()
    return success(playlist.to_dict(), "歌单已更新")


@bp.delete("/<int:playlist_id>")
@login_required
def delete_playlist(playlist_id):
    playlist, err = owned(Playlist, playlist_id, g.current_user.id)
    if err:
        return err
    # 保留歌曲收藏，仅解除归属
    Song.query.filter_by(playlist_id=playlist_id).update(
        {Song.playlist_id: None}, synchronize_session=False
    )
    db.session.delete(playlist)
    db.session.commit()
    return success(None, "歌单已删除，其中歌曲已移至「未分类」")

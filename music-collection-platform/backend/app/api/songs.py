"""歌曲收藏模块：增删改查 + 关键词/标签/歌单筛选。"""
from flask import Blueprint, g, request
from sqlalchemy import or_

from ..extensions import db
from ..models import Playlist, Song, Tag
from ..utils import error, get_json_body, login_required, owned, paginate, success, text

bp = Blueprint("songs", __name__)


def _resolve_playlist(data, uid):
    """校验歌单归属，返回 (playlist_id 或 None, 错误响应)。"""
    raw = data.get("playlistId")
    if raw in (None, "", 0, "0"):
        return None, None
    try:
        pid = int(raw)
    except (TypeError, ValueError):
        return None, error("歌单参数不合法")
    playlist = db.session.get(Playlist, pid)
    if playlist is None or playlist.user_id != uid:
        return None, error("所选歌单不存在")
    return pid, None


def _assign_tags(song, data, uid):
    """按 tagIds 重建歌曲标签关联（只允许用户自己的标签）。"""
    if "tagIds" not in data:
        return
    ids = set()
    for value in data.get("tagIds") or []:
        try:
            ids.add(int(value))
        except (TypeError, ValueError):
            continue
    song.tags = (
        Tag.query.filter(Tag.user_id == uid, Tag.id.in_(ids)).all() if ids else []
    )


def _fill_fields(song, data):
    song.title = text(data, "title")[:200]
    song.artist = text(data, "artist")[:200]
    song.url = text(data, "url")[:1000]
    song.cover = text(data, "cover")[:1000]
    song.notes = text(data, "notes")[:5000]


@bp.get("")
@login_required
def list_songs():
    uid = g.current_user.id
    query = Song.query.filter_by(user_id=uid)

    kw = (request.args.get("kw") or "").strip()
    if kw:
        like = f"%{kw}%"
        query = query.filter(
            or_(
                Song.title.like(like),
                Song.artist.like(like),
                Song.notes.like(like),
                Song.tags.any(Tag.name.like(like)),
            )
        )
    tag_id = request.args.get("tagId", type=int)
    if tag_id:
        query = query.filter(Song.tags.any(Tag.id == tag_id))
    playlist_id = request.args.get("playlistId", type=int)
    if playlist_id:
        query = query.filter(Song.playlist_id == playlist_id)

    query = query.order_by(Song.created_at.desc(), Song.id.desc())
    return success(paginate(query, lambda s: s.to_dict()))


@bp.get("/<int:song_id>")
@login_required
def get_song(song_id):
    song, err = owned(Song, song_id, g.current_user.id)
    if err:
        return err
    return success(song.to_dict())


@bp.post("")
@login_required
def create_song():
    data = get_json_body()
    if not text(data, "title"):
        return error("歌名不能为空")
    uid = g.current_user.id
    playlist_id, err = _resolve_playlist(data, uid)
    if err:
        return err

    song = Song(user_id=uid, playlist_id=playlist_id)
    _fill_fields(song, data)
    _assign_tags(song, data, uid)
    db.session.add(song)
    db.session.commit()
    return success(song.to_dict(), "歌曲已收藏")


@bp.put("/<int:song_id>")
@login_required
def update_song(song_id):
    song, err = owned(Song, song_id, g.current_user.id)
    if err:
        return err
    data = get_json_body()
    if not text(data, "title"):
        return error("歌名不能为空")
    playlist_id, err = _resolve_playlist(data, g.current_user.id)
    if err:
        return err

    _fill_fields(song, data)
    song.playlist_id = playlist_id
    _assign_tags(song, data, g.current_user.id)
    db.session.commit()
    return success(song.to_dict(), "歌曲已更新")


@bp.delete("/<int:song_id>")
@login_required
def delete_song(song_id):
    song, err = owned(Song, song_id, g.current_user.id)
    if err:
        return err
    db.session.delete(song)
    db.session.commit()
    return success(None, "歌曲已删除")

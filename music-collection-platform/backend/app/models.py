"""ORM 数据模型。

四张核心业务表：users / playlists / songs / tags
另加一张 song_tags 关联表（歌曲与标签的多对多关系所必需）。
"""
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


def _now():
    return datetime.now()


def _fmt(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else None


# 歌曲 <-> 标签 多对多关联表
song_tags = db.Table(
    "song_tags",
    db.Column("song_id", db.Integer, db.ForeignKey("songs.id", ondelete="CASCADE"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    db.Column("created_at", db.DateTime, default=_now),
)


class User(db.Model):
    """用户表：role 区分普通用户 / 管理员，status 控制启用状态。"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    nickname = db.Column(db.String(64), nullable=False, default="音乐爱好者")
    email = db.Column(db.String(120), default="")
    avatar = db.Column(db.String(500), default="")
    role = db.Column(db.String(20), nullable=False, default="user")  # user | admin
    status = db.Column(db.SmallInteger, nullable=False, default=1)   # 1 启用 / 0 禁用
    created_at = db.Column(db.DateTime, default=_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now, nullable=False)

    playlists = db.relationship("Playlist", back_populates="user", cascade="all, delete-orphan")
    songs = db.relationship("Song", back_populates="user", cascade="all, delete-orphan")
    tags = db.relationship("Tag", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw):
        return check_password_hash(self.password_hash, raw or "")

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname,
            "email": self.email or "",
            "avatar": self.avatar or "",
            "role": self.role,
            "status": self.status,
            "createdAt": _fmt(self.created_at),
        }


class Playlist(db.Model):
    """歌单表。"""

    __tablename__ = "playlists"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), default="")
    cover = db.Column(db.String(500), default="")
    created_at = db.Column(db.DateTime, default=_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now, nullable=False)

    user = db.relationship("User", back_populates="playlists")
    songs = db.relationship("Song", back_populates="playlist")

    def to_dict(self, song_count=None):
        return {
            "id": self.id,
            "userId": self.user_id,
            "name": self.name,
            "description": self.description or "",
            "cover": self.cover or "",
            "songCount": song_count if song_count is not None else len(self.songs),
            "createdAt": _fmt(self.created_at),
            "updatedAt": _fmt(self.updated_at),
        }


class Song(db.Model):
    """歌曲收藏表。"""

    __tablename__ = "songs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    playlist_id = db.Column(
        db.Integer, db.ForeignKey("playlists.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title = db.Column(db.String(200), nullable=False)
    artist = db.Column(db.String(200), default="")
    url = db.Column(db.String(1000), default="")
    cover = db.Column(db.String(1000), default="")
    notes = db.Column(db.Text, default="")  # 音乐备注
    created_at = db.Column(db.DateTime, default=_now, nullable=False)
    updated_at = db.Column(db.DateTime, default=_now, onupdate=_now, nullable=False)

    user = db.relationship("User", back_populates="songs")
    playlist = db.relationship("Playlist", back_populates="songs")
    tags = db.relationship(
        "Tag", secondary=song_tags, back_populates="songs", lazy="selectin"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "playlistId": self.playlist_id,
            "playlistName": self.playlist.name if self.playlist else "未分类",
            "title": self.title,
            "artist": self.artist or "",
            "url": self.url or "",
            "cover": self.cover or "",
            "notes": self.notes or "",
            "tags": [t.to_dict() for t in self.tags],
            "tagIds": [t.id for t in self.tags],
            "createdAt": _fmt(self.created_at),
            "updatedAt": _fmt(self.updated_at),
        }


class Tag(db.Model):
    """自定义标签表（每个用户拥有自己的标签字典）。"""

    __tablename__ = "tags"
    __table_args__ = (
        db.UniqueConstraint("user_id", "name", name="uk_user_tag"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), nullable=False, default="#7C6BF5")
    created_at = db.Column(db.DateTime, default=_now, nullable=False)

    user = db.relationship("User", back_populates="tags")
    songs = db.relationship("Song", secondary=song_tags, back_populates="tags")

    def to_dict(self, song_count=None):
        return {
            "id": self.id,
            "userId": self.user_id,
            "name": self.name,
            "color": self.color,
            "songCount": song_count if song_count is not None else len(self.songs),
            "createdAt": _fmt(self.created_at),
        }

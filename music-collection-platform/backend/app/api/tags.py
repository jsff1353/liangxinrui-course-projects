"""标签模块：自定义标签、编辑、删除、按标签关联歌曲。"""
import re

from flask import Blueprint, g

from ..extensions import db
from ..models import Tag
from ..utils import error, get_json_body, login_required, owned, success, text

bp = Blueprint("tags", __name__)
COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
DEFAULT_COLORS = ["#7C6BF5", "#4C9AFF", "#36CFC9", "#FF85C0", "#FFA940", "#73D13D"]


def _valid_color(value):
    return COLOR_RE.match(value or "") is not None


@bp.get("")
@login_required
def list_tags():
    tags = (
        Tag.query.filter_by(user_id=g.current_user.id)
        .order_by(Tag.created_at.asc(), Tag.id.asc())
        .all()
    )
    return success([t.to_dict() for t in tags])


@bp.post("")
@login_required
def create_tag():
    data = get_json_body()
    name = text(data, "name")
    if not name:
        return error("标签名称不能为空")
    if len(name) > 50:
        return error("标签名称不能超过 50 个字符")
    uid = g.current_user.id
    if Tag.query.filter_by(user_id=uid, name=name).first():
        return error("该标签已存在")

    color = text(data, "color") or DEFAULT_COLORS[Tag.query.filter_by(user_id=uid).count() % len(DEFAULT_COLORS)]
    if not _valid_color(color):
        return error("颜色格式应为 #RRGGBB")

    tag = Tag(user_id=uid, name=name, color=color)
    db.session.add(tag)
    db.session.commit()
    return success(tag.to_dict(0), "标签创建成功")


@bp.put("/<int:tag_id>")
@login_required
def update_tag(tag_id):
    tag, err = owned(Tag, tag_id, g.current_user.id)
    if err:
        return err
    data = get_json_body()
    name = text(data, "name")
    if not name:
        return error("标签名称不能为空")
    if Tag.query.filter(
        Tag.user_id == g.current_user.id, Tag.name == name, Tag.id != tag_id
    ).first():
        return error("该标签已存在")
    color = text(data, "color") or tag.color
    if not _valid_color(color):
        return error("颜色格式应为 #RRGGBB")

    tag.name = name[:50]
    tag.color = color
    db.session.commit()
    return success(tag.to_dict(), "标签已更新")


@bp.delete("/<int:tag_id>")
@login_required
def delete_tag(tag_id):
    tag, err = owned(Tag, tag_id, g.current_user.id)
    if err:
        return err
    db.session.delete(tag)
    db.session.commit()
    return success(None, "标签已删除，歌曲上的该标签同步移除")

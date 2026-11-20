"""演示数据（歌单 / 标签 / 歌曲）与幂等播种逻辑。

为什么要放在后端而不是只写在 schema.sql 里？
    发行包默认使用零配置 SQLite，启动时由 bootstrap 自动建表，用户不会手工执行
    MySQL 脚本。把演示数据放在这里，可保证「开发模式 / MySQL / SQLite / 打包后的
    exe」四种环境首次启动都能看到一批可试听的示例收藏。

数据与 demo-data.sql（视频录制 / 答辩展示用）保持一致：
    6 个标签 / 3 个歌单 / 8 首歌曲，每首歌都带可播放音频直链
    （SoundHelix 公开测试 MP3），试听按钮不会灰色禁用；封面用 picsum 图片，
    网络不通时界面会自动显示默认封面，不影响演示。

开关：.env 中 SEED_DEMO_DATA=0 可关闭自动播种（默认 1）。
"""
import os
from datetime import timedelta

TAGS = [
    {"name": "轻音乐", "color": "#7C6BF5"},
    {"name": "华语", "color": "#4C9AFF"},
    {"name": "学习专注", "color": "#36CFC9"},
    {"name": "单曲循环", "color": "#FF85C0"},
    {"name": "治愈", "color": "#73D13D"},
    {"name": "通勤", "color": "#FFA940"},
]

PLAYLISTS = [
    {"name": "深夜写代码", "description": "安静、无歌词的专注歌单", "cover": ""},
    {"name": "通勤路上", "description": "随手收藏的华语好歌", "cover": ""},
    {"name": "周末慢时光", "description": "给自己的放松时刻", "cover": ""},
]

# url 以 .mp3 结尾 => 界面判定为音频直链 -> 试听弹窗内可直接播放。
SONGS = [
    {
        "title": "River Flows In You", "artist": "Yiruma", "playlist": "深夜写代码",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        "cover": "https://picsum.photos/seed/river/300/300",
        "tags": ["轻音乐", "学习专注"],
        "notes": "写论文时循环的第一首，钢琴很干净，适合深夜专注。",
    },
    {
        "title": "Kiss The Rain", "artist": "Yiruma", "playlist": "深夜写代码",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
        "cover": "https://picsum.photos/seed/kissrain/300/300",
        "tags": ["轻音乐", "单曲循环"],
        "notes": "雨天氛围感满分，适合一个人的夜晚。",
    },
    {
        "title": "夜的钢琴曲第五号", "artist": "石进", "playlist": "深夜写代码",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
        "cover": "https://picsum.photos/seed/night5/300/300",
        "tags": ["轻音乐", "学习专注"],
        "notes": "简单却耐听，工作间隙放空几分钟。",
    },
    {
        "title": "晴天", "artist": "周杰伦", "playlist": "通勤路上",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3",
        "cover": "https://picsum.photos/seed/sunny/300/300",
        "tags": ["华语", "单曲循环"],
        "notes": "经典回忆，副歌一定要跟唱。",
    },
    {
        "title": "起风了", "artist": "买辣椒也用券", "playlist": "通勤路上",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
        "cover": "https://picsum.photos/seed/wind/300/300",
        "tags": ["华语", "通勤"],
        "notes": "毕业季必听，通勤路上单曲循环。",
    },
    {
        "title": "平凡之路", "artist": "朴树", "playlist": "通勤路上",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3",
        "cover": "https://picsum.photos/seed/road/300/300",
        "tags": ["华语", "治愈"],
        "notes": "歌词很有力量，适合给自己打气。",
    },
    {
        "title": "卡农（钢琴版）", "artist": "Johann Pachelbel", "playlist": "周末慢时光",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3",
        "cover": "https://picsum.photos/seed/canon/300/300",
        "tags": ["轻音乐", "治愈"],
        "notes": "周末午后阳光里的背景音，百听不厌。",
    },
    {
        "title": "稻香", "artist": "周杰伦", "playlist": "周末慢时光",
        "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3",
        "cover": "https://picsum.photos/seed/daoxiang/300/300",
        "tags": ["华语", "治愈"],
        "notes": "轻快的旋律，整理房间时的固定曲目。",
    },
]


def song_rows():
    """统一数据视图：供运行时播种与 SQL 导出共用。"""
    return [
        {
            "title": item["title"],
            "artist": item["artist"],
            "playlist": item["playlist"],
            "url": item["url"],
            "cover": item["cover"],
            "notes": item["notes"],
            "tags": item["tags"],
        }
        for item in SONGS
    ]


def demo_enabled():
    """SEED_DEMO_DATA 默认开启，设为 0 / false / no / off 可关闭。"""
    return os.getenv("SEED_DEMO_DATA", "1").strip().lower() not in ("0", "false", "no", "off")


def seed_demo_data(verbose=False, force=False):
    """给管理员账号补齐演示收藏，幂等且不覆盖用户已有内容。

    默认仅在管理员名下没有任何歌曲时播种；force=True 时仍只补缺失条目，
    不会被重复插入，也不会覆盖用户手工编辑过的歌曲 / 标签 / 歌单。
    """
    from datetime import datetime

    from .extensions import db
    from .models import Playlist, Song, Tag, User

    if not demo_enabled():
        if verbose:
            print("[demo] 演示数据播种已关闭（SEED_DEMO_DATA=0）")
        return {"skipped": True, "reason": "disabled"}

    username = (os.getenv("ADMIN_USERNAME") or "admin").strip()
    admin = User.query.filter_by(username=username).first()
    if admin is None:
        admin = User.query.filter_by(role="admin").order_by(User.id).first()
    if admin is None:
        return {"skipped": True, "reason": "no-admin"}

    uid = admin.id
    existing = Song.query.filter_by(user_id=uid).count()
    if existing and not force:
        if verbose:
            print(f"[demo] 检测到已有 {existing} 首收藏，跳过演示数据播种")
        return {"skipped": True, "reason": "existing", "existing": existing}

    created = {"playlists": 0, "tags": 0, "songs": 0}

    tag_map = {}
    for spec in TAGS:
        tag = Tag.query.filter_by(user_id=uid, name=spec["name"]).first()
        if tag is None:
            tag = Tag(user_id=uid, name=spec["name"], color=spec["color"])
            db.session.add(tag)
            created["tags"] += 1
        tag_map[spec["name"]] = tag
    db.session.flush()

    playlist_map = {}
    for spec in PLAYLISTS:
        playlist = Playlist.query.filter_by(user_id=uid, name=spec["name"]).first()
        if playlist is None:
            playlist = Playlist(
                user_id=uid, name=spec["name"],
                description=spec["description"], cover=spec["cover"],
            )
            db.session.add(playlist)
            created["playlists"] += 1
        playlist_map[spec["name"]] = playlist
    db.session.flush()

    now = datetime.now()
    for index, row in enumerate(song_rows()):
        song = Song.query.filter_by(
            user_id=uid, title=row["title"], artist=row["artist"]
        ).first()
        if song is not None:
            continue
        stamp = now - timedelta(hours=3 * index)  # 让「最近收藏」与列表排序有层次
        song = Song(
            user_id=uid,
            playlist_id=playlist_map[row["playlist"]].id,
            title=row["title"], artist=row["artist"],
            url=row["url"], cover=row["cover"], notes=row["notes"],
            created_at=stamp, updated_at=stamp,
            tags=[tag_map[name] for name in row["tags"]],
        )
        db.session.add(song)
        created["songs"] += 1

    db.session.commit()
    if verbose:
        print(f"[demo] 演示数据就绪：新增 {created['songs']} 首歌曲 / "
              f"{created['playlists']} 个歌单 / {created['tags']} 个标签"
              f"（均带可播放音频直链）")
    return {"skipped": False, **created}


# ---------------------------------------------------------------------------
# 把同一份数据导出为 MySQL 初始化语句，保证 database/schema.sql 与运行时播种一致
# ---------------------------------------------------------------------------
SCHEMA_BEGIN = "-- ==== BEGIN AUTO DEMO DATA ===="
SCHEMA_END = "-- ==== END AUTO DEMO DATA ===="


def _q(value):
    """SQL 字符串转义。"""
    return "'" + str(value).replace("\\", "\\\\").replace("'", "''") + "'"


def export_insert_sql():
    tag_ids = {spec["name"]: i + 1 for i, spec in enumerate(TAGS)}
    playlist_ids = {spec["name"]: i + 1 for i, spec in enumerate(PLAYLISTS)}
    lines = [
        "-- 演示歌单、标签、歌曲（与 backend/app/demo_data.py / demo-data.sql 保持同步）",
        "-- 每首歌均带可播放音频直链；封面为 picsum 图片，网络不通时界面显示默认封面。",
        "INSERT INTO tags (id, user_id, name, color) VALUES",
    ]
    lines.append(",\n".join(
        f"    ({tag_ids[s['name']]}, 1, {_q(s['name'])}, {_q(s['color'])})" for s in TAGS
    ) + ";")
    lines.append("")
    lines.append("INSERT INTO playlists (id, user_id, name, description, cover) VALUES")
    lines.append(",\n".join(
        f"    ({playlist_ids[p['name']]}, 1, {_q(p['name'])}, "
        f"{_q(p['description'])}, {_q(p['cover'])})" for p in PLAYLISTS
    ) + ";")
    lines.append("")
    lines.append("INSERT INTO songs (id, user_id, playlist_id, title, artist, url, cover, notes) VALUES")
    lines.append(",\n".join(
        f"    ({i + 1}, 1, {playlist_ids[r['playlist']]}, {_q(r['title'])}, "
        f"{_q(r['artist'])}, {_q(r['url'])}, {_q(r['cover'])}, {_q(r['notes'])})"
        for i, r in enumerate(song_rows())
    ) + ";")
    lines.append("")
    relations = []
    for i, row in enumerate(song_rows()):
        for name in row["tags"]:
            relations.append(f"    ({i + 1}, {tag_ids[name]})")
    lines.append("INSERT INTO song_tags (song_id, tag_id) VALUES")
    lines.append(",\n".join(relations) + ";")
    return "\n".join(lines)


def sync_schema_sql(path=None):
    """用最新演示数据替换 schema.sql 中两个锚点之间的内容。"""
    if path is None:
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.normpath(os.path.join(here, "..", "..", "database", "schema.sql"))
    with open(path, "r", encoding="utf-8") as fh:
        content = fh.read()
    if SCHEMA_BEGIN not in content or SCHEMA_END not in content:
        raise RuntimeError("schema.sql 中缺少演示数据锚点，无法同步")
    head, rest = content.split(SCHEMA_BEGIN, 1)
    _, tail = rest.split(SCHEMA_END, 1)
    updated = (head + SCHEMA_BEGIN + "\n" + export_insert_sql() + "\n" + SCHEMA_END + tail)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(updated)
    return path

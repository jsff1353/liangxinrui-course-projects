-- =============================================================
--  在线音乐收藏管理桌面平台 —— MySQL 建库建表脚本
--  适用：MySQL 5.7 / 8.0+   字符集：utf8mb4
--  执行：mysql -u root -p < database/schema.sql
--
--  表清单（4 张核心业务表 + 1 张多对多关联表）：
--    users       用户表
--    playlists   歌单表
--    songs       歌曲表
--    tags        标签表
--    song_tags   歌曲-标签关联表（多对多关系所必需，非业务实体表）
-- =============================================================

CREATE DATABASE IF NOT EXISTS music_collection
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE music_collection;

-- 按外键依赖顺序删除（仅用于重复初始化）
DROP TABLE IF EXISTS song_tags;
DROP TABLE IF EXISTS songs;
DROP TABLE IF EXISTS playlists;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS users;

-- -------------------------------------------------------------
-- 1. 用户表
-- -------------------------------------------------------------
CREATE TABLE users (
    id            INT           NOT NULL AUTO_INCREMENT COMMENT '主键',
    username      VARCHAR(64)   NOT NULL                COMMENT '登录用户名（唯一）',
    password_hash VARCHAR(255)  NOT NULL                COMMENT 'Werkzeug 加密后的密码',
    nickname      VARCHAR(64)   NOT NULL DEFAULT '音乐爱好者' COMMENT '昵称',
    email         VARCHAR(120)  NULL     DEFAULT ''     COMMENT '邮箱',
    avatar        VARCHAR(500)  NULL     DEFAULT ''     COMMENT '头像地址',
    role          VARCHAR(20)   NOT NULL DEFAULT 'user' COMMENT '角色：user 普通用户 / admin 管理员',
    status        TINYINT       NOT NULL DEFAULT 1      COMMENT '状态：1 启用 / 0 禁用',
    created_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at    DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_username (username),
    KEY idx_users_role (role)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '用户表';

-- -------------------------------------------------------------
-- 2. 歌单表
-- -------------------------------------------------------------
CREATE TABLE playlists (
    id          INT           NOT NULL AUTO_INCREMENT COMMENT '主键',
    user_id     INT           NOT NULL                COMMENT '所属用户（外键）',
    name        VARCHAR(100)  NOT NULL                COMMENT '歌单名称',
    description VARCHAR(500)  NULL     DEFAULT ''     COMMENT '歌单简介',
    cover       VARCHAR(500)  NULL     DEFAULT ''     COMMENT '封面图片地址',
    created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    KEY idx_playlists_user (user_id),
    CONSTRAINT fk_playlists_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '歌单表';

-- -------------------------------------------------------------
-- 3. 歌曲表
-- -------------------------------------------------------------
CREATE TABLE songs (
    id           INT           NOT NULL AUTO_INCREMENT COMMENT '主键',
    user_id      INT           NOT NULL                COMMENT '收藏人（外键）',
    playlist_id  INT           NULL                    COMMENT '所属歌单（外键，删除歌单时置空保留歌曲）',
    title        VARCHAR(200)  NOT NULL                COMMENT '歌名',
    artist       VARCHAR(200)  NULL     DEFAULT ''     COMMENT '歌手',
    url          VARCHAR(1000) NULL     DEFAULT ''     COMMENT '音乐链接',
    cover        VARCHAR(1000) NULL     DEFAULT ''     COMMENT '封面图片地址',
    notes        TEXT          NULL                    COMMENT '音乐备注',
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (id),
    KEY idx_songs_user (user_id),
    KEY idx_songs_playlist (playlist_id),
    KEY idx_songs_title (title),
    KEY idx_songs_artist (artist),
    CONSTRAINT fk_songs_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT fk_songs_playlist FOREIGN KEY (playlist_id) REFERENCES playlists (id) ON DELETE SET NULL
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '歌曲收藏表';

-- -------------------------------------------------------------
-- 4. 标签表
-- -------------------------------------------------------------
CREATE TABLE tags (
    id         INT          NOT NULL AUTO_INCREMENT COMMENT '主键',
    user_id    INT          NOT NULL                COMMENT '创建人（外键）',
    name       VARCHAR(50)  NOT NULL                COMMENT '标签名称，同一用户下不可重复',
    color      VARCHAR(20)  NOT NULL DEFAULT '#7C6BF5' COMMENT '标签颜色',
    created_at DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (id),
    UNIQUE KEY uk_user_tag (user_id, name),
    KEY idx_tags_user (user_id),
    CONSTRAINT fk_tags_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '标签表';

-- -------------------------------------------------------------
-- 5. 歌曲-标签关联表（实现「给歌曲打多个标签」）
-- -------------------------------------------------------------
CREATE TABLE song_tags (
    song_id    INT      NOT NULL COMMENT '歌曲 ID',
    tag_id     INT      NOT NULL COMMENT '标签 ID',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (song_id, tag_id),
    KEY idx_st_tag (tag_id),
    CONSTRAINT fk_st_song FOREIGN KEY (song_id) REFERENCES songs (id) ON DELETE CASCADE,
    CONSTRAINT fk_st_tag FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '歌曲标签关联表';

-- -------------------------------------------------------------
-- 6. 初始化数据：管理员账号 + 演示数据
--    密码为 admin123（Werkzeug pbkdf2 哈希，可由后端 check_password_hash 校验）
--    生产/答辩前请登录后在「个人中心」修改密码。
--
--    下面锚点之间的演示数据由 backend/app/demo_data.py 统一维护：
--    修改演示歌单 / 标签 / 歌曲后，执行 `python seed_demo.py --sync-schema`
--    即可重新生成，避免 SQL 脚本与运行时自动播种的数据不一致。
--    即使不执行本脚本，直接启动后端也会由 bootstrap 自动建表并播种同样的数据。
-- -------------------------------------------------------------
INSERT INTO users (id, username, password_hash, nickname, email, role, status)
VALUES (1, 'admin', 'pbkdf2:sha256:1000000$u1XXI4buAPWtKt35$369477e424deda06edb5094a20f69161bec9643736863cdfe3201783c2eedc1f', '超级管理员', 'admin@music.local', 'admin', 1);

-- ==== BEGIN AUTO DEMO DATA ====
-- 演示歌单、标签、歌曲（与 backend/app/demo_data.py / demo-data.sql 保持同步）
-- 每首歌均带可播放音频直链；封面为 picsum 图片，网络不通时界面显示默认封面。
INSERT INTO tags (id, user_id, name, color) VALUES
    (1, 1, '轻音乐', '#7C6BF5'),
    (2, 1, '华语', '#4C9AFF'),
    (3, 1, '学习专注', '#36CFC9'),
    (4, 1, '单曲循环', '#FF85C0'),
    (5, 1, '治愈', '#73D13D'),
    (6, 1, '通勤', '#FFA940');

INSERT INTO playlists (id, user_id, name, description, cover) VALUES
    (1, 1, '深夜写代码', '安静、无歌词的专注歌单', ''),
    (2, 1, '通勤路上', '随手收藏的华语好歌', ''),
    (3, 1, '周末慢时光', '给自己的放松时刻', '');

INSERT INTO songs (id, user_id, playlist_id, title, artist, url, cover, notes) VALUES
    (1, 1, 1, 'River Flows In You', 'Yiruma', 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3', 'https://picsum.photos/seed/river/300/300', '写论文时循环的第一首，钢琴很干净，适合深夜专注。'),
    (2, 1, 1, 'Kiss The Rain', 'Yiruma', 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3', 'https://picsum.photos/seed/kissrain/300/300', '雨天氛围感满分，适合一个人的夜晚。'),
    (3, 1, 1, '夜的钢琴曲第五号', '石进', 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3', 'https://picsum.photos/seed/night5/300/300', '简单却耐听，工作间隙放空几分钟。'),
    (4, 1, 2, '晴天', '周杰伦', 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3', 'https://picsum.photos/seed/sunny/300/300', '经典回忆，副歌一定要跟唱。'),
    (5, 1, 2, '起风了', '买辣椒也用券', 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3', 'https://picsum.photos/seed/wind/300/300', '毕业季必听，通勤路上单曲循环。'),
    (6, 1, 2, '平凡之路', '朴树', 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3', 'https://picsum.photos/seed/road/300/300', '歌词很有力量，适合给自己打气。'),
    (7, 1, 3, '卡农（钢琴版）', 'Johann Pachelbel', 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-7.mp3', 'https://picsum.photos/seed/canon/300/300', '周末午后阳光里的背景音，百听不厌。'),
    (8, 1, 3, '稻香', '周杰伦', 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3', 'https://picsum.photos/seed/daoxiang/300/300', '轻快的旋律，整理房间时的固定曲目。');

INSERT INTO song_tags (song_id, tag_id) VALUES
    (1, 1),
    (1, 3),
    (2, 1),
    (2, 4),
    (3, 1),
    (3, 3),
    (4, 2),
    (4, 4),
    (5, 2),
    (5, 6),
    (6, 2),
    (6, 5),
    (7, 1),
    (7, 5),
    (8, 2),
    (8, 5);
-- ==== END AUTO DEMO DATA ====

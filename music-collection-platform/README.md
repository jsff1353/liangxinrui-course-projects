# 在线音乐收藏管理桌面平台

一个轻量化、无广告、专注「歌单 / 收藏 / 标签 / 备注 / 搜索」的音乐收藏管理工具。
标准前后端分离项目，可独立部署 Web 前端，也可用 Electron 打包为 Windows 桌面 exe。

**技术栈**：Python Flask + Vue3 + Vite + Element Plus + MySQL + Electron
**适用**：毕业设计 / 课程设计，代码结构清晰、注释适中、开箱运行。

---

## 一、功能清单

| 模块 | 已实现功能 |
| --- | --- |
| 用户 | 注册、登录、密码加密校验（Werkzeug）、JWT 鉴权、个人信息修改、修改密码、账号禁用、普通用户 / 管理员权限区分 |
| 歌单 | 创建、编辑、删除、列表展示、歌曲数统计、歌单详情、删除歌单时保留歌曲 |
| 歌曲收藏 | 新增（歌名 / 歌手 / 链接 / 封面 / 备注 / 歌单 / 标签）、编辑、删除、按歌单归属、试听、外部链接跳转 |
| 标签 | 自定义标签（名称 + 颜色）、给歌曲打多个标签、按标签筛选、标签重命名 / 删除、关联歌曲数量 |
| 搜索 | 关键词同时匹配歌名、歌手、标签名、备注；可叠加标签 + 歌单筛选；分页 |
| 管理后台 | 平台数据统计、用户搜索 / 启用禁用 / 设管理员 / 删除、全站歌曲与歌单查看、违规内容删除 |
| 桌面端 | Electron 独立窗口、自动拉起随包 Flask 后端、系统浏览器打开外链、NSIS 安装包 + 便携版 |
| 演示数据 | 首次启动自动播种 4 个歌单 / 9 个标签 / 12 首歌曲，其中 8 首为随包内置原创音频，可离线试听 |

---

## 二、目录结构

```text
music-collection-desktop/
├── README.md                     # 本说明文档
├── database/
│   └── schema.sql                # MySQL 建库建表脚本（含管理员与演示数据）
├── tools/
│   └── generate_demo_audio.py    # 演示音频 / SVG 封面生成器（原创合成，可复现）
├── backend/                      # Flask 后端（可独立部署）
│   ├── app/
│   │   ├── __init__.py           # 应用工厂、CORS、JWT 错误处理、/api/health
│   │   ├── bootstrap.py          # 首次启动自动建表 + 管理员 + 演示数据
│   │   ├── config.py             # MySQL / SQLite 配置、.env 读取
│   │   ├── demo_data.py          # 演示数据定义 / 幂等播种 / SQL 导出
│   │   ├── extensions.py         # db / jwt / cors 实例
│   │   ├── models.py             # ORM 模型（users/playlists/songs/tags/song_tags）
│   │   ├── utils.py              # 统一响应、鉴权装饰器、分页、归属校验
│   │   └── api/
│   │       ├── __init__.py       # 蓝图注册
│   │       ├── auth.py           # 注册 / 登录
│   │       ├── users.py          # 个人信息 / 密码 / 首页统计
│   │       ├── playlists.py      # 歌单 CRUD
│   │       ├── songs.py          # 歌曲 CRUD + 搜索筛选
│   │       ├── tags.py           # 标签 CRUD
│   │       └── admin.py          # 管理员后台
│   ├── run.py                    # 后端启动入口
│   ├── init_db.py                # 建表 + 创建管理员 + 演示数据
│   ├── seed_demo.py              # 演示数据工具（补齐 / 导出 SQL / 同步 schema）
│   ├── build_backend.py          # PyInstaller 打包后端为 music-api.exe
│   ├── requirements.txt          # 运行依赖
│   ├── requirements-pack.txt     # 打包依赖
│   └── .env.example              # 配置模板（复制为 .env 使用）
└── frontend/                     # Vue3 前端 + Electron
    ├── package.json              # 依赖、脚本、electron-builder 配置
    ├── vite.config.js            # base:'./'、/api 开发代理
    ├── index.html
    ├── public/demo/              # 内置演示资源（构建时原样复制进 dist）
    │   ├── audio/                # 8 段原创 WAV，离线可直接试听
    │   └── covers/               # 12 张本地 SVG 封面
    ├── electron/
    │   ├── main.cjs              # 主进程：探测/拉起后端、创建窗口、外链处理
    │   ├── preload.cjs           # 安全桥 electronAPI
    │   └── renderer-server.cjs   # 生产模式静态服务（托管 dist，支持 Range）
    ├── scripts/
    │   ├── dev-electron.cjs      # 一键 Vite + Electron 开发
    │   └── prepare-pack.cjs      # 打包前置资源检查
    └── src/
        ├── main.js               # Vue / Pinia / Router / Element Plus 挂载
        ├── App.vue
        ├── styles/main.css       # 全局主题样式
        ├── api/                  # axios 封装 + 各模块接口
        ├── router/index.js       # hash 路由 + 登录与管理员守卫
        ├── store/user.js         # 登录态与用户信息
        ├── layout/index.vue      # 侧边栏 + 顶栏布局
        ├── utils/songActions.js  # 外链打开 / 音频直链判断
        ├── components/           # SongCover / SongForm / SongTable / PlaylistForm / AudioPlayer
        └── views/                # Login / Register / Home / Playlists / PlaylistDetail / Songs / Tags / Profile / Admin
```

---

## 三、环境要求

| 软件 | 版本建议 |
| --- | --- |
| Python | 3.9+（已在 3.13 验证） |
| MySQL | 5.7 / 8.0+（也可用 SQLite 零配置演示） |
| Node.js | 18+（已在 22 验证） |
| 操作系统 | Windows 10/11（Electron 打包目标平台） |

---

## 四、快速开始（开发模式）

### 1. 准备数据库

**方式 A：正式 MySQL 方式**

```bash
# ① 执行 SQL 脚本（会创建数据库、4+1 张表、管理员账号和演示数据）
mysql -u root -p < database/schema.sql

# ② 复制配置并修改数据库账号密码
cd backend
copy .env.example .env        # Windows CMD；PowerShell 用 Copy-Item
# 编辑 .env 里的 DB_HOST / DB_PORT / DB_USER / DB_PASSWORD / DB_NAME
```

> 也可以不执行 SQL 脚本：`python run.py` 首次启动时会自动建表、创建管理员并播种演示数据
> （表结构与 schema.sql 完全一致）。

**方式 B：零配置 SQLite 演示（没装 MySQL 也能跑通全部功能）**

把 `backend/.env` 中 `USE_SQLITE=1`，然后直接启动后端即可。
此模式仅用于本地演示 / 答辩，正式环境请使用 MySQL。

### 2. 启动后端

```bash
cd backend
python -m pip install -r requirements.txt
python run.py              # http://127.0.0.1:5000/api
```

`run.py` 首次运行会自动建表、创建管理员并播种一批演示收藏（已有收藏则跳过，
不会覆盖用户数据），也可单独执行 `python init_db.py` 做显式初始化。
看到 `API 已启动` 即成功，可访问 `http://127.0.0.1:5000/api/health` 检查。

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev                # http://127.0.0.1:5173
```

浏览器打开 `http://127.0.0.1:5173`，用 **admin / admin123**（管理员）或自行注册普通用户登录。
登录后即可看到 4 个演示歌单、9 个标签和 12 首示例歌曲，其中 8 首点「试听」可离线播放
（详见第十节）。

### 4. 以桌面窗口开发调试

```bash
cd frontend
npm run electron:dev       # 自动启动 Vite 并打开 Electron 窗口
```

Electron 启动时先探测 `127.0.0.1:5000`：若已有 Flask 服务则直接连接；
若 `backend-dist/music-api.exe` 存在则自动拉起后端并等待就绪。

---

## 五、数据库设计（4 张业务表 + 1 张关联表）

| 表 | 说明 | 关键字段 / 约束 |
| --- | --- | --- |
| `users` | 用户表 | PK `id`，UK `username`，`password_hash`，`role`(user/admin)，`status`，`created_at`，`updated_at` |
| `playlists` | 歌单表 | PK `id`，FK `user_id → users.id ON DELETE CASCADE`，`name`，`description`，`cover`，时间字段 |
| `songs` | 歌曲表 | PK `id`，FK `user_id → users.id`、`playlist_id → playlists.id ON DELETE SET NULL`，`title`，`artist`，`url`，`cover`，`notes`，时间字段 |
| `tags` | 标签表 | PK `id`，FK `user_id → users.id`，UK(`user_id`,`name`)，`name`，`color`，`created_at` |
| `song_tags` | 歌曲-标签关联表 | 复合主键(`song_id`,`tag_id`)，两个外键均 `ON DELETE CASCADE`，`created_at` |

> 「给歌曲打多个标签」在关系型数据库中必须使用多对多关联表，因此除题目要求的 4 张业务表外，
> 额外提供 1 张 `song_tags` 中间表（不是业务实体表）。全部表均带主键、外键与时间字段。

---

## 六、RESTful 接口一览

统一响应格式：`{ "code": 0, "message": "...", "data": ... }`；
除注册/登录外均需请求头 `Authorization: Bearer <token>`。

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/auth/register` | 用户注册（返回 token） |
| POST | `/api/auth/login` | 用户登录 |
| GET/PUT | `/api/users/me` | 获取 / 修改个人信息 |
| PUT | `/api/users/password` | 修改密码 |
| GET | `/api/users/stats` | 首页统计与最近收藏 |
| GET/POST | `/api/playlists` | 歌单列表 / 创建 |
| GET/PUT/DELETE | `/api/playlists/<id>` | 歌单详情 / 编辑 / 删除 |
| GET/POST | `/api/songs` | 歌曲列表（kw、tagId、playlistId、page、size）/ 新增 |
| GET/PUT/DELETE | `/api/songs/<id>` | 歌曲详情 / 编辑 / 删除 |
| GET/POST | `/api/tags` | 标签列表 / 创建 |
| PUT/DELETE | `/api/tags/<id>` | 编辑 / 删除标签 |
| GET | `/api/admin/overview` | 平台数据统计（管理员） |
| GET | `/api/admin/users` | 用户列表（管理员） |
| PUT | `/api/admin/users/<id>/status` | 启用 / 禁用用户 |
| PUT | `/api/admin/users/<id>/role` | 设置角色 |
| DELETE | `/api/admin/users/<id>` | 删除用户及全部数据 |
| GET | `/api/admin/songs`、`/api/admin/playlists` | 全站内容列表 |
| DELETE | `/api/admin/songs/<id>`、`/api/admin/playlists/<id>` | 违规内容删除 |
| GET | `/api/health` | 健康检查（Electron 探测用） |

---

## 七、Windows 桌面 exe 打包教程

### 第 1 步：把 Flask 后端打包成单文件 exe（可选但推荐）

```bash
cd backend
python -m pip install -r requirements-pack.txt
python build_backend.py
```

产物：`backend-dist/music-api.exe`。

> 若跳过此步，打包出的客户端仍可用，但需要用户本机常驻运行 `python run.py`（或部署远程后端）。

### 第 2 步：确认数据库配置

源码默认连接 MySQL（见 `backend/.env.example`）。**分发包默认启用零配置 SQLite**：
`prepare-pack.cjs` 会把 `backend/.env` 同步到 `backend-dist/.env` 并将 `USE_SQLITE` 置为 1，
数据文件由 Electron 主进程写入用户数据目录，因此安装后双击即可使用，无需先装 MySQL。

要让安装包连接 MySQL：先执行 `database/schema.sql`，再编辑
`安装目录/resources/backend/.env`（或打包前设 `PACK_USE_SQLITE=0`），把 `USE_SQLITE` 改回 0
并填写 `DB_HOST / DB_PORT / DB_USER / DB_PASSWORD / DB_NAME`，重启客户端即可。随包 `README.txt` 亦有说明。

### 第 3 步：构建前端 + 生成安装包

```bash
cd frontend
npm install
npm run pack:win
```

该命令依次执行：`prepare-pack.cjs`（同步 .env、检查后端 exe、写随包说明）→ `vite build` → `electron-builder --win --x64`。

产物位于 `dist-electron/`：

- `MusicCollection Setup 1.0.0.exe`：NSIS 安装包（可选择安装目录、创建桌面快捷方式）
- `MusicCollection-Portable.exe`：免安装便携版
- `win-unpacked/`：未打包目录，可直接运行 `MusicCollection.exe` 调试

窗口与安装包图标取自 `frontend/build/icon.ico`（项目已内置），替换该文件即可换图标。

**国内网络 / 离线打包**：首次打包需联网下载 Electron 运行时和 NSIS 构建工具，建议先设置镜像：

```bash
set ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/
set ELECTRON_BUILDER_BINARIES_MIRROR=https://npmmirror.com/mirrors/electron-builder-binaries/
```

若 Electron 二进制仍下载失败（网络拦截 GitHub），可手动下载
`https://npmmirror.com/mirrors/electron/33.4.11/electron-v33.4.11-win32-x64.zip`，
解压到 `frontend/node_modules/electron/dist/`（确保 `electron.exe` 在该目录下），
并在 `node_modules/electron/path.txt` 写入 `electron.exe`，然后执行：

```bash
npm run pack:win:local
```

该脚本通过 `--config.electronDist` 直接复用本地 Electron 目录，完全跳过运行时下载。

### 打包后的运行逻辑

1. 客户端启动 → 访问 `http://127.0.0.1:5000/api/health`
2. 服务已存在 → 直接连接（支持连接局域网内已部署的后端）
3. 服务不存在 → 自动运行 `resources/backend/music-api.exe` 并等待就绪
4. 由客户端内置的本地静态服务托管 `dist` 页面并加载（端口自动分配，hash 路由，
   避免 `file://` 下 ES Module 的加载限制，无需另行启动 Nginx / Web 服务器）
5. 关闭窗口时自动结束随包后端进程并关闭页面服务
6. 随包后端首次启动会自动建表、创建管理员 `admin / admin123` 并播种演示数据；SQLite 数据文件位于
   `%APPDATA%/music-collection-desktop/music_collection.db`，重装不会覆盖已有数据

---

## 八、常见问题

| 问题 | 处理 |
| --- | --- |
| 后端报 `Can't connect to MySQL server` | 检查 MySQL 是否启动、`.env` 中 `DB_*` 是否正确、数据库是否创建；或临时设 `USE_SQLITE=1` |
| 登录一直提示「无法连接服务器」 | 确认 `python run.py` 在运行、5000 端口未被占用、前端 `/api` 代理或 `VITE_API_BASE_URL` 正确 |
| 端口 5000 被占用 | 修改 `backend/.env` 的 `PORT`，同步 `frontend/vite.config.js` 代理目标与 `frontend/.env` 的 `VITE_API_BASE_URL` |
| Electron 窗口白屏 | 先执行 `npm run build` 确认 `frontend/dist/index.html` 存在；已使用 `base: './'` + hash 路由 + 内置静态服务，勿改为 history 模式 |
| 封面图片不显示 | 需填写 `http(s)://` 开头的图片地址且网络可达；加载失败会自动显示渐变默认封面 |
| 试听没声音 | 只有音频直链（.mp3/.flac/.m4a/.wav/.ogg 等）能直接播放，网页链接请点「链接」用浏览器打开；带「内置音频」标签的 8 首演示曲目是随包 WAV，离线也一定能播 |
| 不想要演示数据 / 想要空白库 | 在 `backend/.env` 设 `SEED_DEMO_DATA=0` 再启动即可关闭自动播种；已播种的内容可在界面删除，但只要把收藏删光，下次启动仍会重新播种 |
| 忘记管理员密码 | 执行 `python init_db.py` 不会覆盖已有账号；可删除 `users` 表中 admin 行后重新执行，或直接改库 |
| 打包后想换数据库 | 编辑 `安装目录/resources/backend/.env`（或 `backend-dist/.env` 后重新打包），重启客户端 |
| 打包时卡在下载 Electron / NSIS | 设置第七节的两个镜像变量；若仍失败，用 `npm run pack:win:local` 复用本地 Electron 目录 |
| 安装包打开后接口报 500 | 默认 `USE_SQLITE=1` 免配置；若改成了 MySQL，需先执行 `schema.sql` 并确认 `DB_*` 正确 |
| 客户端数据存在哪 | 默认 SQLite：`%APPDATA%/music-collection-desktop/music_collection.db`；改 MySQL 后存在数据库中 |
| 重复打包时构建器清空 `win-unpacked` 被安全软件/策略拦截 | 换一个输出目录即可：`electron-builder --win --x64 --config.directories.output=../dist-electron-final` |

---

## 九、默认账号

| 角色 | 用户名 | 密码 |
| --- | --- | --- |
| 管理员 | `admin` | `admin123` |
| 普通用户 | 通过注册页面自行创建 | — |

> 演示环境请登录后及时在「个人中心」修改密码。

---

## 十、演示数据与内置音频

首次启动（或执行 `python init_db.py` / `python seed_demo.py`）会自动给**管理员账号**播种：

| 内容 | 数量 | 说明 |
| --- | --- | --- |
| 歌单 | 4 | 深夜写代码 / 通勤路上 / 周末慢时光 / 纯音乐实验室，均带本地 SVG 封面 |
| 标签 | 9 | 轻音乐 / 华语 / 学习 / 单曲循环 / 钢琴 / 电子 / 氛围 / 治愈 / 内置音频 |
| 歌曲 | 12 | 8 首内置原创音频（可直接试听）+ 4 首外链示例（演示网页链接跳转） |

**为什么点「试听」就能出声？**
`frontend/public/demo/audio/` 下的 8 段 WAV 由 `tools/generate_demo_audio.py`
用 Python 标准库实时合成，是原创的 14~25 秒短曲，不含任何商业录音，可随源码和安装包自由分发；
配合 `frontend/public/demo/covers/` 的 12 张 SVG 封面，答辩现场断网也能完整演示
「封面 / 试听 / 拖动进度条 / 标签筛选 / 搜索」。歌曲的 `url` / `cover` 使用 `./demo/...`
相对路径，由前端静态服务同源托管：Vite 开发服务、`renderer-server.cjs`
（Electron 内置服务，已支持 HTTP Range）、Web 服务器三种环境都能访问，不依赖后端端口，也不需要联网。

> 另外 4 首（Yiruma、周杰伦等）保存的是平台**搜索页**链接，用来演示「网页链接」类型与外链跳转，
> 需要联网；它们点「试听」会提示非音频直链，属于预期行为。

**常用操作**

```bash
cd backend
python seed_demo.py                # 补齐演示数据；已有收藏则跳过，不覆盖用户数据
python seed_demo.py --force        # 已有收藏时也补齐缺失的演示条目
python seed_demo.py --export-sql   # 只打印演示数据的 MySQL INSERT 语句
python seed_demo.py --sync-schema  # 改动演示数据后，同步回 database/schema.sql
```

```bash
cd ..
python tools/generate_demo_audio.py   # 重新生成 8 段 WAV + 12 张 SVG 封面（可复现）
```

**开关**：`backend/.env` 中 `SEED_DEMO_DATA=0` 可关闭自动播种（默认 1）。
播种是幂等的：按名称 / 歌名查重，只补缺失条目，不会覆盖用户编辑过的歌曲、标签或歌单；
普通用户注册后是空白收藏，不受演示数据影响。

演示数据只写入管理员名下；`database/schema.sql` 中的同一批数据由
`python seed_demo.py --sync-schema` 生成并保持一致。打包时 `frontend/public/demo/`
会随 `dist` 一起进入安装包，重装不会覆盖已有的 SQLite 数据文件。

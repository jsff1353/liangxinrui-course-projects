"""把 Flask 后端打包成单文件 music-api.exe（供 Electron 客户端随包分发）。

用法：pip install -r requirements-pack.txt && python build_backend.py
产物：../backend-dist/music-api.exe
"""
import os
import shutil

import PyInstaller.__main__

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(ROOT)
DIST = os.path.join(PROJECT_ROOT, "backend-dist")
BUILD = os.path.join(ROOT, ".build")


def main():
    os.makedirs(DIST, exist_ok=True)
    os.makedirs(BUILD, exist_ok=True)

    # 打包时把配置模板作为默认 .env 一并塞入 exe；用户可在 exe 同目录放 .env 覆盖
    env_file = os.path.join(ROOT, ".env")
    if not os.path.isfile(env_file):
        shutil.copyfile(os.path.join(ROOT, ".env.example"), env_file)
        print("[提示] 已由 .env.example 生成 .env，请按需要修改数据库连接信息")

    args = [
        os.path.join(ROOT, "run.py"),
        "--name", "music-api",
        "--onefile",
        "--noconfirm",
        "--clean",
        "--distpath", DIST,
        "--workpath", BUILD,
        "--specpath", BUILD,
        "--paths", ROOT,
        "--add-data", f"{env_file}{os.pathsep}.",
        "--hidden-import", "pymysql",
        "--hidden-import", "sqlalchemy.dialects.sqlite",
        "--hidden-import", "sqlalchemy.dialects.mysql.pymysql",
        "--hidden-import", "flask_jwt_extended",
        "--hidden-import", "flask_cors",
    ]
    PyInstaller.__main__.run(args)
    print(f"\n[OK] 后端 exe 已生成：{os.path.join(DIST, 'music-api.exe')}")


if __name__ == "__main__":
    main()

"""演示数据命令行工具：python seed_demo.py [选项]

  （无参数）        补齐演示收藏；已有收藏时跳过，不覆盖用户数据
  --force           已有收藏时也补齐缺失的演示条目（仍不覆盖同名歌曲）
  --export-sql      只打印演示数据的 INSERT 语句，不连接数据库
  --sync-schema     把演示数据同步写回 database/schema.sql 的锚点区间

命令行显式执行时忽略 .env 中的 SEED_DEMO_DATA=0 开关，方便手工补数据。
"""
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="音乐收藏演示数据工具")
    parser.add_argument("--force", action="store_true", help="已有收藏时仍补齐缺失的演示条目")
    parser.add_argument("--export-sql", action="store_true", help="导出 MySQL INSERT 语句")
    parser.add_argument("--sync-schema", action="store_true", help="同步到 database/schema.sql")
    args = parser.parse_args()

    if args.export_sql or args.sync_schema:
        from app.demo_data import export_insert_sql, sync_schema_sql
        if args.export_sql:
            print(export_insert_sql())
        if args.sync_schema:
            path = sync_schema_sql()
            print(f"[OK] 演示数据已同步到 {path}", file=sys.stderr)
        return

    # 显式执行本脚本时，临时覆盖「关闭自动播种」的开关（仅影响当前进程）
    os.environ["SEED_DEMO_DATA"] = "1"
    from app import create_app
    from app.bootstrap import initialize
    from app.demo_data import seed_demo_data

    app = create_app()
    initialize(app, verbose=True, seed=False)
    with app.app_context():
        result = seed_demo_data(verbose=True, force=args.force)
    if result.get("reason") == "existing":
        print("提示：如需补齐缺失的演示条目，可执行 python seed_demo.py --force")
    elif result.get("reason") == "no-admin":
        print("[错误] 未找到管理员账号", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()

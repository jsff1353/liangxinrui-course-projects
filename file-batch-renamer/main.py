# -*- coding: utf-8 -*-
"""
================================================================================
文件批量重命名工具  (File Batch Rename Tool)
================================================================================
基于 Python + Tkinter + SQLite 的桌面端文件批量重命名工具，纯本地运行，无需联网。

【项目结构】
    文件批量重命名工具/
    ├── main.py                  程序入口
    ├── requirements.txt         依赖清单
    ├── view/                    界面层
    │   ├── main_window.py       主窗口
    │   ├── dialog_window.py     二级弹窗
    │   └── theme.py             主题样式（配色与 ttk 样式集中管理）
    ├── service/                 业务逻辑层
    │   ├── rename_service.py    重命名核心业务
    │   └── template_service.py  规则模板业务
    ├── dao/                     数据访问层
    │   └── database.py          SQLite 封装（所有 SQL 只在此层）
    ├── db/                      数据存储目录（运行时自动生成 rename_data.db）
    └── resources/               界面资源目录

【运行方式】
    pip install -r requirements.txt
    python main.py

【打包为 exe】
    pyinstaller --noconsole --onefile --name 文件批量重命名工具 main.py
"""

import tkinter as tk
from tkinter import ttk

from dao import database
from view.main_window import RenameApp
from view.theme import apply_theme


def main():
    # 高 DPI 自适应（Windows）
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    # 初始化数据库（建表）
    database.init_db()

    root = Tk_root()
    # 统一应用现代主题样式（须在构建控件之前）
    apply_theme(root)

    app = RenameApp(root)
    root.mainloop()


def Tk_root():
    """创建主窗口（独立出来便于入口清晰）。"""
    return tk.Tk()


if __name__ == '__main__':
    main()

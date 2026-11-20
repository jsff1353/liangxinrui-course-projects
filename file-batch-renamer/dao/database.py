# -*- coding: utf-8 -*-
"""
数据访问层（DAO）
================================================================================
封装 SQLite 数据库连接与所有 SQL 操作。三张表的创建、模板增删改查、操作记录
写入与详情查询全部集中在本层，界面层与业务层不直接编写 SQL。
数据表：
    - rule_template    规则模板表
    - rename_operation 重命名操作主表
    - rename_detail    操作文件详情表
"""

import os
import sys
import sqlite3
import datetime


# ================================================================================
# 路径处理：兼容 PyInstaller 打包后的资源路径（不使用硬编码绝对路径）
# ================================================================================
def get_app_dir():
    """获取程序所在目录：打包后为 exe 所在目录，开发时为项目根目录。"""
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后，sys.executable 指向 exe
        return os.path.dirname(sys.executable)
    # 开发时本文件位于 <项目根>/dao/database.py，上两级即项目根目录
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_db_path():
    """数据库文件路径：放在程序同目录的 db 文件夹下，便于打包后读写。"""
    return os.path.join(get_app_dir(), 'db', 'rename_data.db')


def _connect():
    """建立数据库连接，必要时自动创建 db 目录。"""
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    return sqlite3.connect(db_path)


# ================================================================================
# 数据库初始化：三张表（规则模板 / 重命名操作主表 / 操作文件详情表）
# ================================================================================
def init_db():
    """初始化 SQLite 数据库，建表（已存在则跳过）。"""
    conn = _connect()
    try:
        c = conn.cursor()
        # 表1：规则模板表 —— 保存用户常用的重命名规则配置
        c.execute('''CREATE TABLE IF NOT EXISTS rule_template (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            template_name   TEXT NOT NULL UNIQUE,
            prefix          TEXT DEFAULT '',
            suffix          TEXT DEFAULT '',
            find_str        TEXT DEFAULT '',
            replace_str     TEXT DEFAULT '',
            seq_start       INTEGER DEFAULT 1,
            seq_digit       INTEGER DEFAULT 3,
            seq_position    TEXT DEFAULT '结尾',
            create_time     TEXT NOT NULL
        )''')
        # 表2：重命名操作主表 —— 记录每次批量重命名的整体信息
        c.execute('''CREATE TABLE IF NOT EXISTS rename_operation (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            operate_time    TEXT NOT NULL,
            target_folder   TEXT NOT NULL,
            file_count      INTEGER NOT NULL,
            success_count   INTEGER NOT NULL,
            fail_count      INTEGER NOT NULL,
            remark          TEXT DEFAULT ''
        )''')
        # 表3：操作文件详情表 —— 单次操作每个文件的新旧名映射（撤销功能核心数据）
        c.execute('''CREATE TABLE IF NOT EXISTS rename_detail (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            operation_id    INTEGER NOT NULL,
            old_name        TEXT NOT NULL,
            new_name        TEXT NOT NULL,
            full_path       TEXT NOT NULL,
            status          TEXT NOT NULL,
            FOREIGN KEY (operation_id) REFERENCES rename_operation(id)
        )''')
        conn.commit()
    finally:
        conn.close()


# ================================================================================
# 操作记录：写入与查询
# ================================================================================
def save_operation(result):
    """将一次批量重命名操作记录写入数据库。

    :param result: dict，含 folder/total/success/fail/skip/op_map
    """
    conn = _connect()
    try:
        c = conn.cursor()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute(
            'INSERT INTO rename_operation(operate_time,target_folder,file_count,success_count,fail_count,remark) VALUES (?,?,?,?,?,?)',
            (now, result['folder'], result['total'], result['success'],
             result['fail'] + result['skip'],
             f"成功{result['success']} 失败{result['fail']} 跳过{result['skip']}")
        )
        op_id = c.lastrowid
        for full, old, new, status in result['op_map']:
            c.execute(
                'INSERT INTO rename_detail(operation_id,old_name,new_name,full_path,status) VALUES (?,?,?,?,?)',
                (op_id, old, new, full, status)
            )
        conn.commit()
    finally:
        conn.close()


def list_operations():
    """查询所有操作历史，返回记录行列表。"""
    conn = _connect()
    try:
        c = conn.cursor()
        c.execute('SELECT id,operate_time,target_folder,file_count,success_count,fail_count,remark '
                  'FROM rename_operation ORDER BY id DESC')
        return c.fetchall()
    finally:
        conn.close()


def get_operation_details(op_id):
    """查询指定操作的每个文件新旧名映射。"""
    conn = _connect()
    try:
        c = conn.cursor()
        c.execute('SELECT old_name,new_name,full_path FROM rename_detail WHERE operation_id=?', (op_id,))
        return c.fetchall()
    finally:
        conn.close()


def get_detail_status(op_id):
    """查询指定操作的文件详情（原文件名 / 新文件名 / 状态），用于详情窗口。"""
    conn = _connect()
    try:
        c = conn.cursor()
        c.execute('SELECT old_name,new_name,status FROM rename_detail WHERE operation_id=?', (op_id,))
        return c.fetchall()
    finally:
        conn.close()


# ================================================================================
# 规则模板：增删改查
# ================================================================================
def list_templates():
    """查询所有模板（id, 名称），按 id 倒序。"""
    conn = _connect()
    try:
        c = conn.cursor()
        c.execute('SELECT id,template_name FROM rule_template ORDER BY id DESC')
        return c.fetchall()
    finally:
        conn.close()


def get_template(tid):
    """按 id 查询单个模板完整记录。"""
    conn = _connect()
    try:
        c = conn.cursor()
        c.execute('SELECT * FROM rule_template WHERE id=?', (tid,))
        return c.fetchone()
    finally:
        conn.close()


def insert_template(name, rules):
    """新增规则模板。模板名重复时抛出 sqlite3.IntegrityError。"""
    conn = _connect()
    try:
        c = conn.cursor()
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute(
            'INSERT INTO rule_template(template_name,prefix,suffix,find_str,replace_str,seq_start,seq_digit,seq_position,create_time) '
            'VALUES (?,?,?,?,?,?,?,?,?)',
            (name, rules['prefix'], rules['suffix'], rules['find'], rules['replace'],
             rules['seq_start'], rules['seq_digit'], rules['seq_position'], now)
        )
        conn.commit()
    finally:
        conn.close()


def delete_template(tid):
    """按 id 删除规则模板。"""
    conn = _connect()
    try:
        c = conn.cursor()
        c.execute('DELETE FROM rule_template WHERE id=?', (tid,))
        conn.commit()
    finally:
        conn.close()

# -*- coding: utf-8 -*-
"""
业务逻辑层 —— 规则模板服务
================================================================================
对界面收集的规则配置做校验与组装，调用数据访问层（dao.database）完成模板的
保存、加载、删除，对应「规则模板」「重置规则」功能点。
"""

import datetime

from dao import database


def build_rules_summary(rules):
    """组装模板规则摘要文本，供保存模板弹窗展示。"""
    return (f"前缀：{rules.get('prefix', '')}\n"
            f"后缀：{rules.get('suffix', '')}\n"
            f"查找：{rules.get('find', '')} → 替换：{rules.get('replace', '')}\n"
            f"序号起始：{rules.get('seq_start', 1)} / 位数：{rules.get('seq_digit', 3)} / "
            f"位置：{rules.get('seq_position', '结尾')}")


def save_template(name, rules):
    """保存规则模板。模板名重复时由数据访问层抛出 IntegrityError。"""
    database.insert_template(name, rules)


def list_templates():
    """获取全部模板列表（id, 名称）。"""
    return database.list_templates()


def load_template(tid):
    """加载单个模板完整记录。"""
    return database.get_template(tid)


def delete_template(tid):
    """删除指定模板。"""
    database.delete_template(tid)


def apply_template_to_vars(r, var_setter):
    """
    将模板记录回填到界面变量。
    :param r: 模板记录行
    :param var_setter: 字典，键为规则字段名，值为对应 StringVar 的 set 方法
    """
    var_setter['prefix'](r[2] or '')
    var_setter['suffix'](r[3] or '')
    var_setter['find'](r[4] or '')
    var_setter['replace'](r[5] or '')
    var_setter['seq_start'](str(r[6]))
    var_setter['seq_digit'](str(r[7]))
    var_setter['seq_position'](r[8] or '结尾')

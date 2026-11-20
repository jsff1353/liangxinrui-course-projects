# -*- coding: utf-8 -*-
"""
业务逻辑层 —— 重命名服务
================================================================================
负责重命名核心业务：
    - 按「添加前后缀、字符替换、序号编号」三条规则计算新文件名
    - 重名冲突自动追加序号处理
    - 生成统一的"重命名计划"（预览与执行共用，保证所见即所得）
    - 执行批量重命名
    - 按新旧名映射撤销恢复
"""

import os
import re


def build_new_name(original_name, rules, seq_index):
    """
    根据规则生成新文件名（不含冲突处理）。
    :param original_name: 原文件名（含扩展名）
    :param rules: 规则字典
    :param seq_index: 序号基数（从 0 起），最终序号 = seq_start + seq_index
    :return: 新文件名（含扩展名）

    规则应用顺序：字符替换 → 序号编号 → 添加前后缀 → 拼接扩展名
    """
    # 拆分主文件名与扩展名（如 "IMG_0001.jpg" -> name="IMG_0001", ext=".jpg"）
    name, ext = os.path.splitext(original_name)

    # ---- 1. 字符替换 ----
    find = rules.get('find', '')
    replace = rules.get('replace', '')
    if find:
        if rules.get('case_sensitive', False):
            name = name.replace(find, replace)
        else:
            # 不区分大小写：用正则替换（先转义查找串，避免正则元字符干扰）
            try:
                name = re.sub(re.escape(find),
                              replace.replace('\\', '\\\\'),
                              name, flags=re.IGNORECASE)
            except re.error:
                name = name.replace(find, replace)

    # ---- 2. 序号编号（仅当起始值与位数均已填写有效数字时才生效）----
    seq_start = rules.get('seq_start')
    seq_digit = rules.get('seq_digit')
    if seq_start is not None and seq_digit is not None:
        seq_num = seq_start + seq_index
        if rules.get('leading_zero', True):
            seq_str = str(seq_num).zfill(max(1, seq_digit))
        else:
            seq_str = str(seq_num)
        if rules.get('seq_position', '结尾') == '开头':
            name = seq_str + name
        else:
            name = name + seq_str

    # ---- 3. 添加前后缀 ----
    prefix = rules.get('prefix', '')
    suffix = rules.get('suffix', '')
    if rules.get('ps_position', '扩展名前') == '扩展名前':
        # 后缀放在扩展名前（标准方式）：前缀 + 名称 + 后缀 + 扩展名
        name = prefix + name + suffix
    else:
        # 后缀放在文件名前（紧跟前缀）：前缀 + 后缀 + 名称 + 扩展名
        name = prefix + suffix + name

    return name + ext


def make_unique_name(folder, new_name, current_path, extra_taken=None):
    """
    重名冲突处理：若目标路径已存在且不是当前文件自身，则在主名后追加 _序号，直到唯一。

    :param folder: 目标目录（应为文件自身所在目录，而非统一文件夹）
    :param new_name: 期望的新文件名
    :param current_path: 当前文件完整路径（用于排除"目标就是自己"的情况）
    :param extra_taken: 可选，本批次内已分配给其他文件的新名集合（避免批量内互相冲名）
    :return: 可安全使用的最终新文件名
    """
    extra_taken = extra_taken or set()
    candidate = new_name
    n = 1
    while True:
        candidate_path = os.path.join(folder, candidate)
        exists = os.path.exists(candidate_path)
        is_self = (os.path.normcase(os.path.abspath(candidate_path)) ==
                   os.path.normcase(os.path.abspath(current_path)))
        taken_in_batch = os.path.normcase(candidate) in extra_taken
        if (not exists or is_self) and not taken_in_batch:
            break
        stem, ext = os.path.splitext(new_name)
        candidate = f"{stem}_{n}{ext}"
        n += 1
        if n > 9999:  # 安全上限，避免死循环
            break
    return candidate


def build_rename_plan(files, rules):
    """
    计算本次重命名的完整计划 —— 预览与执行共用此函数，确保"所见即所得"。

    修复点：
      * 序号只对"勾选文件"连续编号（未勾选项不占号），结果写回 f['new_name']；
      * 每个文件在【自身所在目录】内改名，绝不跨目录移动；
      * 冲突处理同时考虑磁盘现状与本批次内已分配的新名。

    :param files: 文件信息字典列表（会被原地更新 new_name 字段）
    :param rules: 规则字典
    :return: plan 列表，每项 dict：{file, old_name, old_path, new_name, new_path, folder}
    """
    # 先清空所有预览名（未勾选项显示 —）
    for f in files:
        f['new_name'] = ''

    assigned_per_folder = {}   # 归一化目录路径 -> 本批次已分配的新名集合
    plan = []
    seq = 0                    # 仅对勾选文件递增，保证序号连续
    for f in files:
        if not f.get('selected'):
            continue
        old_name = f['old_name']
        old_path = f['full']
        folder = os.path.dirname(old_path)          # 关键修复：用文件自身目录
        base_name = build_new_name(old_name, rules, seq)
        seq += 1

        key = os.path.normcase(os.path.abspath(folder))
        taken = assigned_per_folder.setdefault(key, set())
        final_name = make_unique_name(folder, base_name, old_path, extra_taken=taken)
        taken.add(os.path.normcase(final_name))

        f['new_name'] = final_name
        plan.append({
            'file': f,
            'old_name': old_name,
            'old_path': old_path,
            'new_name': final_name,
            'new_path': os.path.join(folder, final_name),
            'folder': folder,
        })
    return plan


def execute_rename(plan, current_folder=''):
    """
    按 build_rename_plan 生成的计划执行批量重命名（在子线程中调用）。

    :param plan: build_rename_plan 返回的计划列表
    :param current_folder: 界面当前文件夹，仅用于写入操作记录的备注字段
    :return: dict 结果统计（success/fail/skip/op_map/folder/total）
    """
    op_map = []          # (old_path, old_name, new_name, status)
    success, fail, skip = 0, 0, 0

    for item in plan:
        old_path = item['old_path']
        old_name = item['old_name']
        new_name = item['new_name']
        final_path = item['new_path']
        try:
            if os.path.normcase(os.path.abspath(old_path)) == \
               os.path.normcase(os.path.abspath(final_path)):
                # 名称实际未变化，跳过
                skip += 1
                op_map.append((old_path, old_name, new_name, '跳过'))
                continue
            os.rename(old_path, final_path)
            success += 1
            op_map.append((old_path, old_name, new_name, '成功'))
            # 更新内存中的文件信息
            f = item['file']
            f['full'] = final_path
            f['old_name'] = new_name
        except Exception as e:
            fail += 1
            op_map.append((old_path, old_name, new_name, f'失败:{e}'))

    return {
        'op_map': op_map, 'success': success, 'fail': fail, 'skip': skip,
        'folder': current_folder, 'total': len(plan)
    }


def build_undo_map(op_map):
    """从操作映射中提取"成功"项，供撤销使用。"""
    return [(full, old, new) for full, old, new, status in op_map if status == '成功']


def undo_mapping(op_map):
    """
    撤销一步：根据新旧名映射恢复文件名（在子线程中调用）。
    :param op_map: 元素 (full_path, old_name, new_name)
    """
    success, fail = 0, 0
    for full_path, old_name, new_name in reversed(op_map):
        folder = os.path.dirname(full_path)
        candidate = os.path.join(folder, new_name)
        try:
            if os.path.exists(candidate):
                src = candidate
            else:
                src = full_path
            dst = os.path.join(folder, old_name)
            if os.path.normcase(os.path.abspath(src)) == os.path.normcase(os.path.abspath(dst)):
                continue
            os.rename(src, dst)
            success += 1
        except Exception:
            fail += 1
    return {'success': success, 'fail': fail}


def undo_by_details(rows):
    """
    根据数据库查询出的详情行撤销指定历史操作（在子线程中调用）。
    :param rows: (old_name, new_name, full_path) 列表
    """
    return undo_mapping([(full, old, new) for old, new, full in rows])

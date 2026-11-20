# -*- coding: utf-8 -*-
"""
界面层 —— 各类二级弹窗
================================================================================
负责各类二级弹窗，对应「操作二次确认」「规则模板保存/选择」「操作历史查看」。
所有数据库访问均通过 dao.database 封装函数完成，界面不直接编写 SQL。
"""

import tkinter as tk
from tkinter import ttk, messagebox, StringVar

from dao import database
from view.theme import Theme, dialog_header, center_dialog


# ================================================================================
# 弹窗：重命名确认弹窗
# ================================================================================
class ConfirmRenameDialog:
    def __init__(self, parent, count, folder, checked):
        self.result = False
        self.dlg = tk.Toplevel(parent)
        self.dlg.title('确认开始重命名')
        self.dlg.transient(parent)
        self.dlg.grab_set()
        self.dlg.resizable(False, False)
        self.dlg.configure(bg=Theme.CARD)

        dialog_header(self.dlg, '确认开始重命名', subtitle='请核对以下信息后再执行',
                      color=Theme.WARNING)

        # 提示内容
        top = ttk.Frame(self.dlg, padding=(20, 16, 20, 8), style='Card.TFrame')
        top.pack(fill='x')
        ttk.Label(top, text='⚠', font=('Arial', 24), foreground=Theme.WARNING).pack(side='left', padx=(0, 14))
        info = ttk.Frame(top, style='Card.TFrame')
        info.pack(side='left')
        ttk.Label(info, text='即将对选中文件执行批量重命名：',
                  style='Section.TLabel').pack(anchor='w')
        ttk.Label(info, text=f'待处理文件数量：{count} 个',
                  style='Field.TLabel').pack(anchor='w', pady=(8, 0))
        ttk.Label(info, text=f'目标文件夹：{folder}',
                  style='Field.TLabel').pack(anchor='w')
        sample = checked[0]['new_name'] if checked and checked[0].get('new_name') else '（点击预览后可见）'
        ttk.Label(info, text=f'示例新文件名：{sample}',
                  style='Field.TLabel').pack(anchor='w', pady=(8, 0))
        ttk.Label(info, text='提示：执行后将修改实际文件名，请确认已完成预览。',
                  foreground=Theme.DANGER).pack(anchor='w', pady=(10, 0))

        # 按钮
        btns = ttk.Frame(self.dlg, padding=(20, 8, 20, 18), style='Card.TFrame')
        btns.pack(fill='x')
        ttk.Button(btns, text='取消', command=self.cancel).pack(side='right', padx=4)
        ttk.Button(btns, text='确认执行', style='Primary.TButton',
                   command=self.ok).pack(side='right', padx=4)

        self.dlg.protocol('WM_DELETE_WINDOW', self.cancel)
        center_dialog(self.dlg, parent)
        self.dlg.wait_window()

    def ok(self):
        self.result = True
        self.dlg.destroy()

    def cancel(self):
        self.result = False
        self.dlg.destroy()


# ================================================================================
# 弹窗：保存规则模板
# ================================================================================
class TemplateSaveDialog:
    def __init__(self, parent, rules, summary):
        self.result = None
        self.rules = rules
        self.dlg = tk.Toplevel(parent)
        self.dlg.title('保存规则模板')
        self.dlg.transient(parent)
        self.dlg.grab_set()
        self.dlg.resizable(False, False)
        self.dlg.configure(bg=Theme.CARD)

        dialog_header(self.dlg, '保存规则模板', subtitle='将当前规则保存为本地模板，方便下次一键调用')

        top = ttk.Frame(self.dlg, padding=(20, 16, 20, 4), style='Card.TFrame')
        top.pack(fill='x')
        ttk.Label(top, text='模板名称', style='Section.TLabel').pack(anchor='w')

        body = ttk.Frame(self.dlg, padding=(20, 6, 20, 8), style='Card.TFrame')
        body.pack(fill='x')
        ttk.Label(body, text='名称：', style='Field.TLabel').grid(row=0, column=0, sticky='e', pady=6)
        self.name_var = StringVar()
        ttk.Entry(body, textvariable=self.name_var, width=30).grid(row=0, column=1, sticky='w', pady=6, padx=8)

        # 规则摘要（由 service 层组装）
        ttk.Label(body, text='规则摘要：', style='Field.TLabel').grid(row=1, column=0, sticky='ne', pady=6)
        box = tk.Label(body, text=summary, justify='left', anchor='w',
                       bg=Theme.SURFACE, fg=Theme.TEXT_SUB, font=(Theme.FONT, 9),
                       highlightthickness=1, highlightbackground=Theme.BORDER, padx=10, pady=8)
        box.grid(row=1, column=1, sticky='w', pady=6, padx=8)

        btns = ttk.Frame(self.dlg, padding=(20, 8, 20, 18), style='Card.TFrame')
        btns.pack(fill='x')
        ttk.Button(btns, text='取消', command=self.cancel).pack(side='right', padx=4)
        ttk.Button(btns, text='确定保存', style='Primary.TButton',
                   command=self.ok).pack(side='right', padx=4)

        self.dlg.protocol('WM_DELETE_WINDOW', self.cancel)
        center_dialog(self.dlg, parent)
        self.dlg.wait_window()

    def ok(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning('提示', '请输入模板名称。', parent=self.dlg)
            return
        self.result = name
        self.dlg.destroy()

    def cancel(self):
        self.result = None
        self.dlg.destroy()


# ================================================================================
# 弹窗：选择模板（加载/删除通用）
# ================================================================================
class TemplatePickDialog:
    def __init__(self, parent, rows, title):
        self.result = None
        self.dlg = tk.Toplevel(parent)
        self.dlg.title(title)
        self.dlg.transient(parent)
        self.dlg.grab_set()
        self.dlg.resizable(False, False)
        self.dlg.configure(bg=Theme.CARD)

        dialog_header(self.dlg, title, subtitle='从已保存的模板中选择一项')

        body = ttk.Frame(self.dlg, padding=(20, 16, 20, 8), style='Card.TFrame')
        body.pack(fill='both', expand=True)
        ttk.Label(body, text='模板列表：', style='Section.TLabel').pack(anchor='w', pady=(0, 8))

        listframe = ttk.Frame(body, style='Card.TFrame')
        listframe.pack(fill='both', expand=True)
        self.listbox = tk.Listbox(listframe, height=9, width=42, activestyle='dotbox',
                                  bg='#FFFFFF', fg=Theme.TEXT_SUB,
                                  selectbackground=Theme.PRIMARY, selectforeground='#FFFFFF',
                                  relief='flat', highlightthickness=1,
                                  highlightbackground=Theme.BORDER,
                                  font=(Theme.FONT, 10))
        self.listbox.pack(side='left', fill='both', expand=True)
        sb = ttk.Scrollbar(listframe, orient='vertical', command=self.listbox.yview)
        sb.pack(side='right', fill='y')
        self.listbox.config(yscrollcommand=sb.set)
        self.rows = rows
        for tid, name in rows:
            self.listbox.insert('end', f'  #{tid}   {name}')
        if rows:
            self.listbox.selection_set(0)
        self.listbox.bind('<Double-Button-1>', lambda e: self.ok())

        btns = ttk.Frame(self.dlg, padding=(20, 8, 20, 18), style='Card.TFrame')
        btns.pack(fill='x')
        ttk.Button(btns, text='取消', command=self.cancel).pack(side='right', padx=4)
        ttk.Button(btns, text='确定', style='Primary.TButton',
                   command=self.ok).pack(side='right', padx=4)

        self.dlg.protocol('WM_DELETE_WINDOW', self.cancel)
        center_dialog(self.dlg, parent)
        self.dlg.wait_window()

    def ok(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning('提示', '请先选择一个模板。', parent=self.dlg)
            return
        idx = sel[0]
        self.result = self.rows[idx][0]
        self.dlg.destroy()

    def cancel(self):
        self.result = None
        self.dlg.destroy()


# ================================================================================
# 弹窗：操作历史窗口
# ================================================================================
class HistoryDialog:
    def __init__(self, parent, app):
        self.app = app
        self.dlg = tk.Toplevel(parent)
        self.dlg.title('操作历史')
        self.dlg.transient(parent)
        self.dlg.geometry('800x460')
        self.dlg.grab_set()
        self.dlg.configure(bg=Theme.CARD)

        dialog_header(self.dlg, '操作历史', subtitle='查看以往的重命名记录，可对指定操作进行撤销')

        body = ttk.Frame(self.dlg, padding=(14, 12), style='Card.TFrame')
        body.pack(fill='both', expand=True)

        cols = ('time', 'folder', 'count', 'result')
        self.tree = ttk.Treeview(body, columns=cols, show='headings', height=12)
        for cid, title, width in [('time', '操作时间', 160),
                                   ('folder', '操作文件夹', 300),
                                   ('count', '文件数量', 90),
                                   ('result', '结果', 200)]:
            self.tree.heading(cid, text=title)
            self.tree.column(cid, width=width, anchor='w', stretch=False)
        self.tree.tag_configure('hasfail', foreground=Theme.DANGER)
        vsb = ttk.Scrollbar(body, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

        btns = ttk.Frame(self.dlg, padding=(14, 6, 14, 16), style='Card.TFrame')
        btns.pack(fill='x')
        ttk.Button(btns, text='查看详情', command=self.view_detail).pack(side='left', padx=4)
        ttk.Button(btns, text='撤销该次操作', command=self.undo_op).pack(side='left', padx=4)
        ttk.Button(btns, text='关闭', command=self.dlg.destroy).pack(side='right', padx=4)

        self.load_data()
        self.dlg.protocol('WM_DELETE_WINDOW', self.dlg.destroy)
        center_dialog(self.dlg, parent)
        self.dlg.wait_window()

    def load_data(self):
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        try:
            rows = database.list_operations()
        except Exception as e:
            messagebox.showerror('错误', f'读取历史失败：\n{e}', parent=self.dlg)
            return
        for r in rows:
            result = f"成功 {r[4]}，失败 {r[5]}"
            tags = ('hasfail',) if r[5] else ()
            self.tree.insert('', 'end', iid=str(r[0]),
                             values=(r[1], r[2], r[3], result), tags=tags)

    def _selected_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning('提示', '请先选择一条操作记录。', parent=self.dlg)
            return None
        return int(sel[0])

    def view_detail(self):
        op_id = self._selected_id()
        if op_id is None:
            return
        try:
            rows = database.get_detail_status(op_id)
        except Exception as e:
            messagebox.showerror('错误', f'读取详情失败：\n{e}', parent=self.dlg)
            return
        if not rows:
            messagebox.showinfo('详情', '该操作无文件详情记录。', parent=self.dlg)
            return
        # 弹出详情子窗口
        sub = tk.Toplevel(self.dlg)
        sub.title(f'操作 #{op_id} 详情')
        sub.geometry('680x400')
        sub.configure(bg=Theme.CARD)
        dialog_header(sub, f'操作 #{op_id} 详情', subtitle='本次操作涉及的文件与新旧名称')

        tbl = ttk.Frame(sub, padding=(12, 12), style='Card.TFrame')
        tbl.pack(fill='both', expand=True)
        t = ttk.Treeview(tbl, columns=('old', 'new', 'status'), show='headings', height=14)
        for cid, title, w in [('old', '原文件名', 230), ('new', '新文件名', 230), ('status', '状态', 120)]:
            t.heading(cid, text=title)
            t.column(cid, width=w, anchor='w', stretch=False)
        t.tag_configure('ok', foreground=Theme.SUCCESS)
        t.tag_configure('bad', foreground=Theme.DANGER)
        t.pack(fill='both', expand=True, side='left')
        ssb = ttk.Scrollbar(tbl, orient='vertical', command=t.yview)
        ssb.pack(side='right', fill='y')
        t.configure(yscrollcommand=ssb.set)
        for old, new, status in rows:
            tag = ('ok',) if status == '成功' else (('bad',) if status.startswith('失败') else ())
            t.insert('', 'end', values=(old, new, status), tags=tag)
        center_dialog(sub, self.dlg)

    def undo_op(self):
        op_id = self._selected_id()
        if op_id is None:
            return
        if not messagebox.askyesno('撤销确认', f'确定撤销操作 #{op_id}？\n将把该次操作的文件恢复为原名。', parent=self.dlg):
            return
        self.dlg.destroy()
        self.app.undo_operation(op_id)

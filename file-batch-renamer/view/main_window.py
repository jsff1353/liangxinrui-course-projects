# -*- coding: utf-8 -*-
"""
界面层 —— 主窗口
================================================================================
负责主窗口的布局与交互：顶部工具栏、文件列表区、三列规则设置区、底部操作栏。
业务计算委托给 service 层，数据持久化委托给 dao 层，界面不直接编写 SQL。
"""

import os
import sys
import threading
import subprocess
import datetime
import tkinter as tk

from tkinter import (
    ttk, filedialog, messagebox,
    StringVar, BooleanVar, DISABLED, NORMAL
)

try:
    from openpyxl import Workbook
    OPENPYXL_OK = True
except Exception:
    OPENPYXL_OK = False

from service import rename_service, template_service
from view import dialog_window
from view.theme import (
    Theme, BrandHeader, add_section_title,
)


class RenameApp:
    # 列定义（与 Treeview 列对应）
    COLUMNS = [('sel', '选择', 50, 'center'),
               ('old', '原文件名', 220, 'w'),
               ('new', '新文件名(预览)', 220, 'w'),
               ('size', '大小', 80, 'e'),
               ('type', '类型', 70, 'center'),
               ('time', '修改时间', 140, 'center')]

    def __init__(self, root):
        self.root = root
        self.root.title("文件批量重命名工具")
        self.root.geometry("1200x940")
        self.root.minsize(1040, 800)

        # 文件列表数据：每项 dict(path, old_name, new_name, size, type, mtime, selected, full)
        self.files = []
        self.current_folder = ''
        # 撤销栈：支持连续多步撤销。每项为一次成功重命名的映射列表
        # 元素结构: [(full_path, old_name, new_name), ...]
        self.undo_stack = []
        self.sort_key = 'old'
        self.sort_asc = True
        # 运行中禁用按钮的标志
        self.busy = False

        # 规则相关变量
        self._init_vars()
        # 构建 UI
        self._build_menu()
        self._build_header()
        self._build_toolbar()
        self._build_file_list()
        self._build_rules()
        # 先建状态栏再建操作栏：pack 到 bottom 时先建者更靠下，状态栏应贴底
        self._build_status_bar()
        self._build_action_bar()

    # ---------- 品牌头部 ----------
    def _build_header(self):
        self.header = BrandHeader(self.root)

    # ---------- 变量定义 ----------
    def _init_vars(self):
        self.prefix_var = StringVar()
        self.suffix_var = StringVar()
        self.ps_pos_var = StringVar(value='扩展名前')
        self.find_var = StringVar()
        self.replace_var = StringVar()
        self.case_var = BooleanVar(value=False)
        self.seq_start_var = StringVar(value='')
        self.seq_digit_var = StringVar(value='')
        self.seq_pos_var = StringVar(value='结尾')
        self.leadzero_var = BooleanVar(value=True)
        self.filter_var = StringVar()
        self.dir_var = StringVar(value='当前目录：未选择')

    # ---------- 菜单栏 ----------
    def _build_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        m_file = tk.Menu(menubar, tearoff=0)
        m_file.add_command(label='退出', command=self.root.quit)
        menubar.add_cascade(label='文件', menu=m_file)

        m_tpl = tk.Menu(menubar, tearoff=0)
        m_tpl.add_command(label='保存规则模板', command=self.save_template)
        m_tpl.add_command(label='加载规则模板', command=self.load_template)
        m_tpl.add_command(label='删除规则模板', command=self.delete_template)
        menubar.add_cascade(label='模板', menu=m_tpl)

        m_hist = tk.Menu(menubar, tearoff=0)
        m_hist.add_command(label='操作历史', command=self.open_history)
        menubar.add_cascade(label='历史', menu=m_hist)

        m_help = tk.Menu(menubar, tearoff=0)
        m_help.add_command(label='关于', command=self.show_about)
        menubar.add_cascade(label='帮助', menu=m_help)

    # ---------- 顶部工具栏（卡片） ----------
    def _build_toolbar(self):
        card = ttk.Frame(self.root, style='Block.TFrame', padding=(16, 12))
        card.pack(fill='x', padx=16, pady=(14, 6))

        ttk.Button(card, text='  ⊕  选择文件夹 ',
                   style='Primary.TButton', command=self.choose_folder).pack(side='left')
        ttk.Button(card, text='  ↻  刷新列表', command=self.refresh_list).pack(side='left', padx=(10, 0))
        ttk.Button(card, text='  ＋  添加文件', command=self.add_files).pack(side='left', padx=(8, 0))
        ttk.Button(card, text='  ⤢  打开所在目录', command=self.open_folder).pack(side='left', padx=(8, 0))

        pill = tk.Frame(card, bg=Theme.SURFACE, highlightthickness=1,
                        highlightbackground=Theme.BORDER)
        pill.pack(side='right')
        tk.Label(pill, text='📁', bg=Theme.SURFACE, font=(Theme.FONT, 10)).pack(side='left', padx=(10, 4), pady=5)
        self.dir_label = ttk.Label(pill, textvariable=self.dir_var, style='Muted.TLabel')
        self.dir_label.pack(side='right', padx=(2, 12), pady=5)
        self.dir_label.configure(background=Theme.SURFACE)

    # ---------- 文件列表区（卡片） ----------
    def _build_file_list(self):
        wrap = ttk.Frame(self.root, style='Block.TFrame', padding=(14, 12))
        wrap.pack(fill='both', expand=True, padx=16, pady=6)

        # 标题行：版块名 + 文件数量徽标
        title_row = ttk.Frame(wrap, style='Card.TFrame')
        title_row.pack(fill='x', pady=(0, 10))
        add_section_title(title_row, '文件列表').pack(side='left')
        self.count_var = StringVar(value='共 0 个文件')
        self.count_label = tk.Label(title_row, textvariable=self.count_var,
                                    bg=Theme.PRIMARY_SOFT, fg=Theme.PRIMARY_DARK,
                                    font=(Theme.FONT, 9, 'bold'), padx=10, pady=2)
        self.count_label.pack(side='right')

        # 快捷操作栏
        top = ttk.Frame(wrap, style='Surface.TFrame')
        top.pack(fill='x', pady=(0, 8), ipady=6, ipadx=6)
        ttk.Button(top, text='全选', width=7, command=lambda: self.set_all_selected(True)).pack(side='left')
        ttk.Button(top, text='反选', width=7, command=self.invert_selected).pack(side='left', padx=6)
        ttk.Button(top, text='清空选择', width=9, command=lambda: self.set_all_selected(False)).pack(side='left')
        sep = tk.Frame(top, bg=Theme.BORDER, width=1, height=22)
        sep.pack(side='left', padx=14, pady=2)
        ttk.Label(top, text='后缀筛选：', style='Muted.TLabel').pack(side='left', padx=(0, 4))
        ent = ttk.Entry(top, textvariable=self.filter_var, width=11)
        ent.pack(side='left')
        ent.bind('<Return>', lambda e: self.apply_filter())
        ttk.Button(top, text='筛选', width=6, command=self.apply_filter).pack(side='left', padx=6)
        ttk.Button(top, text='显示全部', width=9, command=self.clear_filter).pack(side='left')

        # 表格（Treeview + 滚动条）
        col_frame = ttk.Frame(wrap, style='Card.TFrame')
        col_frame.pack(fill='both', expand=True)

        cols = [c[0] for c in self.COLUMNS]
        # height 设小些作为最小高度，实际由 expand+fill 撑满，避免内容溢出窗口
        self.tree = ttk.Treeview(col_frame, columns=cols, show='headings',
                                 selectmode='none', height=6)
        for cid, title, width, anchor in self.COLUMNS:
            self.tree.heading(cid, text=title, command=lambda k=cid: self.sort_by(k))
            self.tree.column(cid, width=width, anchor=anchor, stretch=False)
        # 斑马纹与预览着色标签
        self.tree.tag_configure('oddrow', background=Theme.ROW_ODD)
        self.tree.tag_configure('evenrow', background=Theme.ROW_EVEN)
        self.tree.tag_configure('preview', foreground=Theme.PRIMARY_DARK,
                                font=(Theme.FONT, 10, 'bold'))
        self.tree.tag_configure('unselected', foreground=Theme.MUTED)

        vsb = ttk.Scrollbar(col_frame, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(col_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        col_frame.rowconfigure(0, weight=1)
        col_frame.columnconfigure(0, weight=1)

        # 点击勾选列切换选中状态
        self.tree.bind('<Button-1>', self._on_tree_click)

    def _on_tree_click(self, event):
        """点击「选择」列时切换勾选状态。"""
        region = self.tree.identify('region', event.x, event.y)
        if region != 'cell':
            return
        col = self.tree.identify_column(event.x)
        if col != '#1':  # 第1列即「选择」列
            return
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        idx = int(iid)
        if 0 <= idx < len(self.files):
            f = self.files[idx]
            f['selected'] = not f['selected']
            self.tree.set(iid, 'sel', '☑' if f['selected'] else '☐')
            tags = list(self.tree.item(iid, 'tags'))
            if f['selected']:
                tags = [t for t in tags if t != 'unselected']
            else:
                tags.append('unselected')
            self.tree.item(iid, tags=tags)
            checked = sum(1 for x in self.files if x['selected'])
            self.count_var.set(f'共 {len(self.files)} 个文件 · 已勾选 {checked}')

    # ---------- 规则设置区（三列并排，卡片式） ----------
    def _rule_card(self, parent, step, title, color):
        """创建一张规则卡片：顶部彩色标题条 + 白色内容区，返回 (卡片外层, 内容区)。"""
        card = tk.Frame(parent, bg=Theme.CARD, highlightthickness=1,
                        highlightbackground=Theme.BORDER)
        header = tk.Frame(card, bg=color, height=34)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text=f' {step}  ', bg=color, fg='#FFFFFF',
                 font=(Theme.FONT, 11, 'bold'), padx=8).pack(side='left')
        tk.Label(header, text=title, bg=color, fg='#FFFFFF',
                 font=(Theme.FONT, 10, 'bold')).pack(side='left', padx=(0, 8))
        body = ttk.Frame(card, style='Card.TFrame', padding=(12, 12, 12, 10))
        body.pack(fill='both', expand=True)
        return card, body

    def _build_rules(self):
        wrap = ttk.Frame(self.root, style='Block.TFrame', padding=(14, 12))
        wrap.pack(fill='x', padx=16, pady=6)
        title_row = ttk.Frame(wrap, style='Card.TFrame')
        title_row.pack(fill='x', pady=(0, 10))
        add_section_title(title_row, '重命名规则').pack(side='left')
        ttk.Label(title_row, text='规则可叠加使用，设置后点击「预览效果」查看',
                  style='Muted.TLabel').pack(side='right')

        inner = ttk.Frame(wrap, style='Card.TFrame')
        inner.pack(fill='x')
        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(1, weight=1)
        inner.columnconfigure(2, weight=1)

        # ---- 卡片1：添加前后缀 ----
        card1, c1 = self._rule_card(inner, '①', '添加前后缀', Theme.PRIMARY)
        card1.grid(row=0, column=0, sticky='nsew', padx=(0, 8))
        c1.columnconfigure(1, weight=1)
        ttk.Label(c1, text='前缀：', style='Field.TLabel').grid(row=0, column=0, sticky='e', pady=4)
        ttk.Entry(c1, textvariable=self.prefix_var).grid(row=0, column=1, sticky='ew', pady=4, padx=6)
        ttk.Label(c1, text='后缀：', style='Field.TLabel').grid(row=1, column=0, sticky='e', pady=4)
        ttk.Entry(c1, textvariable=self.suffix_var).grid(row=1, column=1, sticky='ew', pady=4, padx=6)
        ttk.Label(c1, text='位置：', style='Field.TLabel').grid(row=2, column=0, sticky='e', pady=4)
        rf = ttk.Frame(c1, style='Card.TFrame')
        rf.grid(row=2, column=1, sticky='w', pady=4, padx=6)
        ttk.Radiobutton(rf, text='扩展名前', variable=self.ps_pos_var, value='扩展名前').pack(side='left')
        ttk.Radiobutton(rf, text='文件名前', variable=self.ps_pos_var, value='文件名前').pack(side='left', padx=8)

        # ---- 卡片2：字符替换 ----
        card2, c2 = self._rule_card(inner, '②', '字符替换', '#0891B2')
        card2.grid(row=0, column=1, sticky='nsew', padx=8)
        c2.columnconfigure(1, weight=1)
        ttk.Label(c2, text='查找内容：', style='Field.TLabel').grid(row=0, column=0, sticky='e', pady=4)
        ttk.Entry(c2, textvariable=self.find_var).grid(row=0, column=1, sticky='ew', pady=4, padx=6)
        ttk.Label(c2, text='替换为：', style='Field.TLabel').grid(row=1, column=0, sticky='e', pady=4)
        ttk.Entry(c2, textvariable=self.replace_var).grid(row=1, column=1, sticky='ew', pady=4, padx=6)
        ttk.Checkbutton(c2, text='区分大小写', variable=self.case_var).grid(row=2, column=1, sticky='w', pady=4, padx=6)

        # ---- 卡片3：序号编号 ----
        card3, c3 = self._rule_card(inner, '③', '序号编号', '#7C3AED')
        card3.grid(row=0, column=2, sticky='nsew', padx=(8, 0))
        c3.columnconfigure(1, weight=1)
        ttk.Label(c3, text='起始值：', style='Field.TLabel').grid(row=0, column=0, sticky='e', pady=4)
        ttk.Entry(c3, textvariable=self.seq_start_var, width=6).grid(row=0, column=1, sticky='w', pady=4, padx=6)
        ttk.Label(c3, text='位数：', style='Field.TLabel').grid(row=1, column=0, sticky='e', pady=4)
        ttk.Entry(c3, textvariable=self.seq_digit_var, width=6).grid(row=1, column=1, sticky='w', pady=4, padx=6)
        ttk.Label(c3, text='序号位置：', style='Field.TLabel').grid(row=2, column=0, sticky='e', pady=4)
        rf3 = ttk.Frame(c3, style='Card.TFrame')
        rf3.grid(row=2, column=1, sticky='w', pady=4, padx=6)
        ttk.Radiobutton(rf3, text='开头', variable=self.seq_pos_var, value='开头').pack(side='left')
        ttk.Radiobutton(rf3, text='结尾', variable=self.seq_pos_var, value='结尾').pack(side='left', padx=8)
        ttk.Checkbutton(c3, text='前导补零', variable=self.leadzero_var).grid(row=3, column=1, sticky='w', pady=4, padx=6)

    # ---------- 底部操作栏（卡片） ----------
    def _build_action_bar(self):
        bar = ttk.Frame(self.root, style='Block.TFrame', padding=(14, 12))
        bar.pack(fill='x', side='bottom', padx=16, pady=(6, 0))
        ttk.Button(bar, text='↺  重置规则', command=self.reset_rules).pack(side='left', padx=4)
        ttk.Button(bar, text='▣  保存模板', command=self.save_template).pack(side='left', padx=4)
        ttk.Button(bar, text='⇩  导出对照表', command=self.export_excel).pack(side='left', padx=4)
        ttk.Button(bar, text='撤销上一步', command=self.undo_last).pack(side='right', padx=4)
        ttk.Button(bar, text='预览效果', style='Soft.TButton', command=self.preview).pack(side='right', padx=6)
        self.btn_rename = ttk.Button(bar, text='  ✓  开始重命名  ',
                                     style='Primary.TButton', command=self.confirm_rename)
        self.btn_rename.pack(side='right', padx=4)

    # ---------- 状态栏 ----------
    def _build_status_bar(self):
        bar = tk.Frame(self.root, bg='#E8ECF3', height=38)
        bar.pack(fill='x', side='bottom', padx=16, pady=(6, 4))
        bar.pack_propagate(False)
        self.status_dot = tk.Label(bar, text='●', bg='#E8ECF3', fg=Theme.SUCCESS,
                                   font=(Theme.FONT, 10))
        self.status_dot.pack(side='left', padx=(12, 6))
        tk.Label(bar, text='状态', bg='#E8ECF3', fg=Theme.MUTED,
                 font=(Theme.FONT, 9, 'bold')).pack(side='left', padx=(0, 10))
        self.status = ttk.Label(bar, text='就绪，请选择文件夹开始。', anchor='w',
                                style='Status.TLabel')
        self.status.configure(background='#E8ECF3')
        self.status.pack(side='left', fill='x', expand=True)
        tk.Label(bar, text='纯本地运行 · 数据不上传', bg='#E8ECF3', fg=Theme.MUTED,
                 font=(Theme.FONT, 9)).pack(side='right', padx=(0, 12))

    # ====================== 工具方法 ======================
    def set_status(self, text):
        """更新状态文字，并根据关键词切换状态点颜色。"""
        self.status.config(text=text)
        low = str(text)
        color = Theme.SUCCESS
        if any(k in low for k in ('失败', '出错', '错误')):
            color = Theme.DANGER
        elif any(k in low for k in ('正在', '加载', '处理中')):
            color = Theme.WARNING
        self.status_dot.configure(fg=color)

    def set_busy(self, busy):
        """运行耗时操作时禁用主操作按钮，避免重复点击。"""
        self.busy = busy
        state = DISABLED if busy else NORMAL
        for w in self.root.winfo_children():
            self._set_widget_state(w, state)

    def _set_widget_state(self, widget, state):
        try:
            widget.configure(state=state)
        except Exception:
            pass
        for child in widget.winfo_children():
            self._set_widget_state(child, state)

    def run_thread(self, func, done=None):
        """在子线程执行耗时函数 func，完成后在主线程回调 done(result)。"""
        def worker():
            try:
                result = func()
            except Exception as e:
                result = e
            if done is not None:
                self.root.after(0, lambda: done(result))
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    def get_rules(self):
        """从界面控件收集规则配置，返回字典。"""
        def to_int_or_none(v):
            """空值或非法值返回 None（表示该项未配置，序号编号不生效）。"""
            try:
                return int(v)
            except (ValueError, TypeError):
                return None
        return {
            'prefix': self.prefix_var.get(),
            'suffix': self.suffix_var.get(),
            'ps_position': self.ps_pos_var.get(),
            'find': self.find_var.get(),
            'replace': self.replace_var.get(),
            'case_sensitive': self.case_var.get(),
            'seq_start': to_int_or_none(self.seq_start_var.get()),
            'seq_digit': to_int_or_none(self.seq_digit_var.get()),
            'seq_position': self.seq_pos_var.get(),
            'leading_zero': self.leadzero_var.get(),
        }

    # ====================== 文件导入 ======================
    def choose_folder(self):
        folder = filedialog.askdirectory(title='选择文件夹')
        if not folder:
            return
        self.current_folder = folder
        self.dir_var.set(f'当前目录：{folder}')
        self.load_folder(folder)

    def load_folder(self, folder):
        """扫描文件夹下所有文件（子线程，避免阻塞 UI）。"""
        self.set_status('正在加载文件列表…')
        self.set_busy(True)

        def work():
            items = []
            try:
                for fn in os.listdir(folder):
                    full = os.path.join(folder, fn)
                    if not os.path.isfile(full):
                        continue
                    # 跳过隐藏文件（Windows 下以 . 开头或带隐藏属性）
                    if fn.startswith('.'):
                        continue
                    try:
                        st = os.stat(full)
                    except Exception:
                        continue
                    items.append({
                        'path': folder,
                        'full': full,
                        'old_name': fn,
                        'new_name': '',
                        'size': st.st_size,
                        'type': os.path.splitext(fn)[1].lower().lstrip('.') or '文件',
                        'mtime': st.st_mtime,
                        'selected': True,
                    })
            except Exception as e:
                return e
            return items

        def done(result):
            self.set_busy(False)
            if isinstance(result, Exception):
                self.set_status(f'加载失败：{result}')
                messagebox.showerror('错误', f'加载文件夹失败：\n{result}')
                return
            self.files = result
            self.populate_tree()
            self.set_status(f'已加载 {len(self.files)} 个文件。')

        self.run_thread(work, done)

    def refresh_list(self):
        if not self.current_folder:
            messagebox.showinfo('提示', '请先选择文件夹。')
            return
        self.load_folder(self.current_folder)

    def add_files(self):
        """添加零散文件到列表，可混合不同目录。"""
        files = filedialog.askopenfilenames(title='选择一个或多个文件')
        if not files:
            return
        existing = {f['full'] for f in self.files}
        added = 0
        for full in files:
            if full in existing:
                continue
            try:
                st = os.stat(full)
            except Exception:
                continue
            fn = os.path.basename(full)
            self.files.append({
                'path': os.path.dirname(full),
                'full': full,
                'old_name': fn,
                'new_name': '',
                'size': st.st_size,
                'type': os.path.splitext(fn)[1].lower().lstrip('.') or '文件',
                'mtime': st.st_mtime,
                'selected': True,
            })
            added += 1
        self.populate_tree()
        self.set_status(f'新增 {added} 个文件，当前共 {len(self.files)} 个。')

    def open_folder(self):
        if not self.current_folder:
            messagebox.showinfo('提示', '请先选择文件夹。')
            return
        try:
            # Windows 用 explorer 打开
            if sys.platform.startswith('win'):
                os.startfile(self.current_folder)  # type: ignore[attr-defined]
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', self.current_folder])
            else:
                subprocess.Popen(['xdg-open', self.current_folder])
        except Exception as e:
            messagebox.showerror('错误', f'无法打开目录：\n{e}')

    # ====================== 列表渲染与筛选 ======================
    def populate_tree(self):
        """把 self.files 渲染到表格。"""
        # 清空旧行
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for i, f in enumerate(self.files):
            tags = ('evenrow' if i % 2 else 'oddrow',)
            if not f['selected']:
                tags += ('unselected',)
            if f['new_name']:
                tags += ('preview',)
            self.tree.insert('', 'end', iid=str(i), values=(
                '☑' if f['selected'] else '☐',
                f['old_name'],
                f['new_name'] or '—',
                self._human_size(f['size']),
                f['type'],
                self._format_time(f['mtime']),
            ), tags=tags)
        checked = sum(1 for f in self.files if f['selected'])
        self.count_var.set(f'共 {len(self.files)} 个文件 · 已勾选 {checked}')

    def _human_size(self, num):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if num < 1024.0:
                if unit == 'B':
                    return f"{int(num)} B"
                return f"{num:.1f} {unit}"
            num /= 1024.0
        return f"{num:.1f} TB"

    def _format_time(self, ts):
        try:
            return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M')
        except Exception:
            return str(ts)

    def apply_filter(self):
        kw = self.filter_var.get().strip().lower().lstrip('.')
        if not kw:
            self.populate_tree()
            return
        # 仅显示匹配后缀的文件
        for iid in self.tree.get_children():
            self.tree.delete(iid)
        for i, f in enumerate(self.files):
            ext = os.path.splitext(f['old_name'])[1].lower().lstrip('.')
            if ext == kw:
                tags = ('evenrow' if i % 2 else 'oddrow',)
                if not f['selected']:
                    tags += ('unselected',)
                if f['new_name']:
                    tags += ('preview',)
                self.tree.insert('', 'end', iid=str(i), values=(
                    '☑' if f['selected'] else '☐',
                    f['old_name'], f['new_name'] or '—',
                    self._human_size(f['size']), f['type'], self._format_time(f['mtime']),
                ), tags=tags)
        self.count_var.set(f'筛选 .{kw} · 显示 {len(self.tree.get_children())} 个')
        self.set_status(f'筛选后缀 .{kw}：显示 {len(self.tree.get_children())} 个文件。')

    def clear_filter(self):
        self.filter_var.set('')
        self.populate_tree()

    def _sync_selection_tags(self):
        """根据 files 数据的 selected 状态，刷新可见行的图标、淡化样式与计数。"""
        for iid in self.tree.get_children():
            idx = int(iid)
            if idx >= len(self.files):
                continue
            f = self.files[idx]
            self.tree.set(iid, 'sel', '☑' if f['selected'] else '☐')
            tags = list(self.tree.item(iid, 'tags'))
            tags = [t for t in tags if not t.startswith(('oddrow', 'evenrow', 'unselected', 'preview'))]
            base = ('evenrow' if idx % 2 else 'oddrow',)
            if not f['selected']:
                base += ('unselected',)
            if f['new_name']:
                base += ('preview',)
            self.tree.item(iid, tags=base)
        checked = sum(1 for f in self.files if f['selected'])
        self.count_var.set(f'共 {len(self.files)} 个文件 · 已勾选 {checked}')

    def set_all_selected(self, value):
        for f in self.files:
            f['selected'] = value
        self._sync_selection_tags()
        self.set_status(f'已{"全选" if value else "清空"}所有文件。')

    def invert_selected(self):
        for f in self.files:
            f['selected'] = not f['selected']
        self._sync_selection_tags()
        self.set_status('已反选。')

    # ====================== 排序 ======================
    def sort_by(self, key):
        if self.sort_key == key:
            self.sort_asc = not self.sort_asc
        else:
            self.sort_key = key
            self.sort_asc = True
        reverse = not self.sort_asc

        def keyfunc(f):
            if key == 'old':
                return f['old_name'].lower()
            if key == 'new':
                return (f['new_name'] or '').lower()
            if key == 'size':
                return f['size']
            if key == 'type':
                return f['type'].lower()
            if key == 'time':
                return f['mtime']
            return ''
        self.files.sort(key=keyfunc, reverse=reverse)
        self.populate_tree()
        self.set_status(f'已按{"升序" if self.sort_asc else "降序"}排序（{key}）。')

    # ====================== 预览 ======================
    def preview(self):
        """根据当前规则生成新文件名（含冲突处理），仅更新列表显示，不修改磁盘。"""
        if not self.files:
            messagebox.showinfo('提示', '请先导入文件。')
            return
        rules = self.get_rules()
        # 预览与执行共用同一套计划逻辑，保证"所见即所得"
        rename_service.build_rename_plan(self.files, rules)
        self.populate_tree()
        self.set_status('预览已生成（未修改磁盘文件）。')

    # ====================== 执行重命名 ======================
    def confirm_rename(self):
        if self.busy:
            return
        checked = [f for f in self.files if f['selected']]
        if not checked:
            messagebox.showwarning('提示', '请先勾选需要重命名的文件。')
            return
        if not self.current_folder:
            messagebox.showwarning('提示', '请先选择目标文件夹。')
            return
        # 生成计划（含冲突处理与预览名），确保弹窗示例与最终结果一致
        rules = self.get_rules()
        plan = rename_service.build_rename_plan(self.files, rules)
        self.populate_tree()

        # 二次确认弹窗（示例取计划中的最终新名）
        dlg = dialog_window.ConfirmRenameDialog(self.root, len(checked), self.current_folder, checked)
        if not dlg.result:
            return
        self._do_rename(plan)

    def _do_rename(self, plan):
        """子线程执行批量重命名。"""
        self.set_busy(True)
        self.set_status('正在批量重命名…')

        def work():
            return rename_service.execute_rename(plan, self.current_folder)

        def done(result):
            self.set_busy(False)
            if isinstance(result, Exception):
                self.set_status(f'重命名出错：{result}')
                messagebox.showerror('错误', f'重命名出错：\n{result}')
                return
            # 仅把"成功"的项压入撤销栈，支持连续多步撤销
            undo_map = rename_service.build_undo_map(result['op_map'])
            if undo_map:
                self.undo_stack.append(undo_map)
            # 写入数据库（通过 dao 层）
            try:
                from dao import database
                database.save_operation(result)
            except Exception as e:
                print(f'[DB] 保存操作记录失败：{e}')
            self.populate_tree()
            msg = f"重命名完成：成功 {result['success']}，失败 {result['fail']}，跳过 {result['skip']}。"
            self.set_status(msg)
            messagebox.showinfo('重命名结果', msg)

        self.run_thread(work, done)

    # ====================== 撤销 ======================
    def undo_last(self):
        if not self.undo_stack:
            messagebox.showinfo('提示', '没有可撤销的操作。')
            return
        # 取栈顶（最近一步），但不立即弹出——执行成功后再弹出
        op_map = list(self.undo_stack[-1])
        if not messagebox.askyesno('撤销确认', '确定撤销最近一次重命名操作？\n（将把文件名恢复为原名）'):
            return
        self.set_busy(True)
        self.set_status('正在撤销…')

        def work():
            return rename_service.undo_mapping(op_map)

        def done(result):
            self.set_busy(False)
            if isinstance(result, Exception):
                self.set_status(f'撤销出错：{result}')
                messagebox.showerror('错误', f'撤销出错：\n{result}')
                return
            # 成功撤销后弹出栈顶，可继续撤销更早的一步
            self.undo_stack.pop()
            # 重新加载当前目录文件以刷新列表
            if self.current_folder:
                self.load_folder(self.current_folder)
            self.set_status(f"撤销完成：恢复 {result['success']} 个，失败 {result['fail']} 个。\n"
                            f"还可撤销 {len(self.undo_stack)} 步。")
            messagebox.showinfo('撤销结果',
                                f"恢复 {result['success']} 个，失败 {result['fail']} 个。")

        self.run_thread(work, done)

    # ====================== 导出 Excel 对照表 ======================
    def export_excel(self):
        if not self.files:
            messagebox.showinfo('提示', '当前没有文件可导出。')
            return
        if not OPENPYXL_OK:
            messagebox.showerror('错误', '未安装 openpyxl，无法导出 Excel。\n请执行：pip install openpyxl')
            return
        path = filedialog.asksaveasfilename(
            title='保存对照表', defaultextension='.xlsx',
            filetypes=[('Excel 文件', '*.xlsx')],
            initialfile=f'重命名对照表_{datetime.datetime.now():%Y%m%d_%H%M%S}.xlsx'
        )
        if not path:
            return
        self.set_busy(True)
        self.set_status('正在导出对照表…')

        def work():
            wb = Workbook()
            ws = wb.active
            ws.title = '重命名对照表'
            ws.append(['序号', '原文件名', '新文件名', '大小', '类型', '修改时间', '状态'])
            for i, f in enumerate(self.files, 1):
                ws.append([
                    i, f['old_name'], f['new_name'] or '',
                    f['size'], f['type'], self._format_time(f['mtime']),
                    '已勾选' if f['selected'] else '未勾选',
                ])
            # 列宽
            for col, w in zip('ABCDEFG', [6, 26, 26, 12, 10, 20, 10]):
                ws.column_dimensions[col].width = w
            wb.save(path)
            return path

        def done(result):
            self.set_busy(False)
            if isinstance(result, Exception):
                self.set_status(f'导出失败：{result}')
                messagebox.showerror('错误', f'导出失败：\n{result}')
                return
            self.set_status(f'对照表已导出：{result}')
            messagebox.showinfo('导出成功', f'对照表已保存：\n{result}')

        self.run_thread(work, done)

    # ====================== 规则模板 ======================
    def save_template(self):
        import sqlite3
        rules = self.get_rules()
        dlg = dialog_window.TemplateSaveDialog(
            self.root, rules, template_service.build_rules_summary(rules))
        if not dlg.result:
            return
        name = dlg.result
        try:
            template_service.save_template(name, rules)
            self.set_status(f'模板「{name}」已保存。')
            messagebox.showinfo('成功', f'模板「{name}」已保存。')
        except sqlite3.IntegrityError:
            messagebox.showerror('错误', f'模板名「{name}」已存在，请换一个名称。')
        except Exception as e:
            messagebox.showerror('错误', f'保存模板失败：\n{e}')

    def load_template(self):
        try:
            rows = template_service.list_templates()
        except Exception as e:
            messagebox.showerror('错误', f'读取模板失败：\n{e}')
            return
        if not rows:
            messagebox.showinfo('提示', '暂无已保存的模板。')
            return
        dlg = dialog_window.TemplatePickDialog(self.root, rows, '加载模板')
        if not dlg.result:
            return
        tid = dlg.result
        try:
            r = template_service.load_template(tid)
        except Exception as e:
            messagebox.showerror('错误', f'加载模板失败：\n{e}')
            return
        if r:
            template_service.apply_template_to_vars(r, {
                'prefix': self.prefix_var.set,
                'suffix': self.suffix_var.set,
                'find': self.find_var.set,
                'replace': self.replace_var.set,
                'seq_start': self.seq_start_var.set,
                'seq_digit': self.seq_digit_var.set,
                'seq_position': self.seq_pos_var.set,
            })
            self.set_status(f'已加载模板「{r[1]}」。')
            messagebox.showinfo('成功', f'已加载模板「{r[1]}」。')

    def delete_template(self):
        try:
            rows = template_service.list_templates()
        except Exception as e:
            messagebox.showerror('错误', f'读取模板失败：\n{e}')
            return
        if not rows:
            messagebox.showinfo('提示', '暂无模板可删除。')
            return
        dlg = dialog_window.TemplatePickDialog(self.root, rows, '删除模板')
        if not dlg.result:
            return
        tid = dlg.result
        try:
            template_service.delete_template(tid)
            self.set_status('模板已删除。')
            messagebox.showinfo('成功', '模板已删除。')
        except Exception as e:
            messagebox.showerror('错误', f'删除模板失败：\n{e}')

    def reset_rules(self):
        self.prefix_var.set('')
        self.suffix_var.set('')
        self.ps_pos_var.set('扩展名前')
        self.find_var.set('')
        self.replace_var.set('')
        self.case_var.set(False)
        self.seq_start_var.set('')
        self.seq_digit_var.set('')
        self.seq_pos_var.set('结尾')
        self.leadzero_var.set(True)
        self.set_status('规则已重置。')

    # ====================== 操作历史 ======================
    def open_history(self):
        dialog_window.HistoryDialog(self.root, self)

    # ====================== 关于 ======================
    def show_about(self):
        messagebox.showinfo('关于',
                            '文件批量重命名工具\n'
                            'Python 3.10 + Tkinter + SQLite\n'
                            '课程结课作业 · 单人开发\n'
                            '功能：批量改名 / 预览 / 撤销 / 导出对照表 / 规则模板 / 操作历史')

    # 历史窗口撤销指定操作时回调
    def undo_operation(self, op_id):
        """根据数据库 operation_id 撤销指定历史操作。"""
        from dao import database
        self.set_busy(True)
        self.set_status(f'正在撤销操作 #{op_id}…')

        def work():
            try:
                rows = database.get_operation_details(op_id)
            except Exception as e:
                return e
            return rename_service.undo_by_details(rows)

        def done(result):
            self.set_busy(False)
            if isinstance(result, Exception):
                self.set_status(f'撤销出错：{result}')
                messagebox.showerror('错误', f'撤销出错：\n{result}')
                return
            if self.current_folder:
                self.load_folder(self.current_folder)
            self.set_status(f"撤销操作 #{op_id}：恢复 {result['success']} 个，失败 {result['fail']} 个。")
            messagebox.showinfo('撤销结果',
                                f"恢复 {result['success']} 个，失败 {result['fail']} 个。")

        self.run_thread(work, done)

# -*- coding: utf-8 -*-
"""
界面层 —— 主题样式
================================================================================
集中管理界面配色与 ttk 样式（现代扁平卡片风格，纯标准库实现，无第三方依赖）。

设计语言：以 slate 中性灰为底，indigo 靛蓝为主色，辅以清爽的青色点缀，
通过「深顶栏 + 白卡片 + 细描边 + 强调色按钮」构建层次分明的现代桌面界面。

所有颜色定义在 Theme 类中，便于整体换肤；apply_theme() 须在创建控件前调用。
本模块同时提供若干自绘 UI 组件（品牌头部、版块标题、圆角矩形）与弹窗工具，
供 main_window.py / dialog_window.py 共用。
"""

import tkinter as tk
from tkinter import ttk


class Theme:
    """集中管理界面配色与字体，便于整体换肤。"""
    # 主色 —— 靛蓝
    PRIMARY       = '#4F46E5'   # 主色-靛蓝
    PRIMARY_DARK  = '#4338CA'   # 主色-深
    PRIMARY_SOFT  = '#EEF2FF'   # 主色-浅底（悬停/聚焦）
    PRIMARY_MID   = '#6366F1'   # 主色-中
    # 顶部品牌栏
    HEADER_BG     = '#312E81'   # 深靛蓝顶栏
    HEADER_ACCENT = '#818CF8'   # 顶栏强调文字（浅靛）
    # 中性色 —— slate
    BG            = '#F1F5F9'   # 窗口底色 slate-100
    CARD          = '#FFFFFF'   # 卡片底色
    SURFACE       = '#F8FAFC'   # 次级表面 slate-50
    BORDER        = '#E2E8F0'   # 浅描边 slate-200
    OUTLINE       = '#CBD5E1'   # 主描边 slate-300
    OUTLINE_LIGHT = '#E2E8F0'   # 表格描边
    TEXT          = '#0F172A'   # 主文字 slate-900
    TEXT_SUB      = '#334155'   # 次级文字 slate-700
    MUTED         = '#64748B'   # 次要文字 slate-500
    SUCCESS       = '#10B981'   # 成功绿 emerald
    WARNING       = '#F59E0B'   # 警告橙 amber
    DANGER        = '#EF4444'   # 危险红 red
    PREVIEW       = '#0E7490'   # 预览列着色 cyan-700
    ROW_ODD       = '#FFFFFF'   # 斑马纹-白
    ROW_EVEN      = '#F8FAFC'   # 斑马纹-浅灰
    FONT          = 'Microsoft YaHei UI'


def _mix(hex_color, target, ratio):
    """按比例将 hex_color 向 target 混合，用于生成悬停/按下等衍生色。"""
    h = hex_color.lstrip('#')
    t = target.lstrip('#')
    r1, g1, b1 = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    r2, g2, b2 = int(t[0:2], 16), int(t[2:4], 16), int(t[4:6], 16)
    r = int(r1 + (r2 - r1) * ratio)
    g = int(g1 + (g2 - g1) * ratio)
    b = int(b1 + (b2 - b1) * ratio)
    return f'#{r:02X}{g:02X}{b:02X}'


def apply_theme(root):
    """配置全局 ttk 样式；须在创建任何控件之前调用。返回 Style 对象。"""
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except Exception:
        pass
    F = Theme.FONT

    # ---------- 基础 ----------
    style.configure('.', font=(F, 10), foreground=Theme.TEXT, background=Theme.BG)
    style.configure('TFrame', background=Theme.BG)
    style.configure('Card.TFrame', background=Theme.CARD, relief='flat')
    style.configure('Block.TFrame', background=Theme.CARD, relief='solid',
                    borderwidth=1, bordercolor=Theme.BORDER)
    style.configure('Surface.TFrame', background=Theme.SURFACE, relief='flat')

    # ---------- 标签 ----------
    style.configure('TLabel', background=Theme.BG, foreground=Theme.TEXT)
    style.configure('Card.TLabel', background=Theme.CARD)
    style.configure('Muted.TLabel', background=Theme.CARD, foreground=Theme.MUTED)
    style.configure('Section.TLabel', background=Theme.CARD, foreground=Theme.PRIMARY_DARK,
                    font=(F, 10, 'bold'))
    style.configure('Field.TLabel', background=Theme.CARD, foreground=Theme.TEXT_SUB)

    # ---------- 按钮 ----------
    style.configure('TButton', font=(F, 10), padding=(11, 6), relief='flat',
                    background=Theme.CARD, foreground=Theme.TEXT_SUB,
                    borderwidth=1, bordercolor=Theme.OUTLINE)
    style.map('TButton',
              background=[('active', Theme.PRIMARY_SOFT), ('pressed', '#DDE4FF')],
              foreground=[('active', Theme.PRIMARY_DARK)],
              bordercolor=[('active', Theme.PRIMARY_MID)])
    style.configure('Primary.TButton', font=(F, 10, 'bold'), padding=(14, 8),
                    background=Theme.PRIMARY, foreground='#FFFFFF',
                    borderwidth=0, relief='flat')
    style.map('Primary.TButton',
              background=[('active', Theme.PRIMARY_DARK), ('pressed', Theme.PRIMARY_DARK)],
              foreground=[('active', '#FFFFFF')])
    style.configure('Soft.TButton', font=(F, 10, 'bold'), padding=(12, 7),
                    background=Theme.PRIMARY_SOFT, foreground=Theme.PRIMARY_DARK,
                    borderwidth=1, bordercolor=Theme.PRIMARY_MID, relief='flat')
    style.map('Soft.TButton',
              background=[('active', '#DDE4FF'), ('pressed', '#D3DCFF')],
              foreground=[('active', Theme.PRIMARY_DARK)])

    # ---------- 分组框（卡片） ----------
    style.configure('TLabelframe', background=Theme.CARD, bordercolor=Theme.BORDER,
                    relief='solid', borderwidth=1)
    style.configure('TLabelframe.Label', background=Theme.CARD,
                    foreground=Theme.PRIMARY_DARK, font=(F, 10, 'bold'))

    # ---------- 输入框 ----------
    style.configure('TEntry', fieldbackground='#FFFFFF', bordercolor=Theme.OUTLINE,
                    padding=(7, 5), relief='flat')
    style.map('TEntry', bordercolor=[('focus', Theme.PRIMARY)],
              fieldbackground=[('focus', '#FFFFFF')])

    # ---------- 复选 / 单选 ----------
    style.configure('TCheckbutton', background=Theme.CARD, font=(F, 10),
                    foreground=Theme.TEXT_SUB)
    style.map('TCheckbutton', background=[('active', Theme.CARD)])
    style.configure('TRadiobutton', background=Theme.CARD, font=(F, 10),
                    foreground=Theme.TEXT_SUB)
    style.map('TRadiobutton', background=[('active', Theme.CARD)])

    # ---------- 表格 ----------
    style.configure('Treeview', font=(F, 10), rowheight=30, background=Theme.CARD,
                    fieldbackground=Theme.CARD, bordercolor=Theme.BORDER,
                    relief='flat', borderwidth=1)
    style.configure('Treeview.Heading', font=(F, 10, 'bold'), background='#EEF2FF',
                    foreground=Theme.PRIMARY_DARK, relief='flat', padding=(8, 7))
    style.map('Treeview.Heading', background=[('active', '#DDE4FF')])

    # ---------- 滚动条 ----------
    style.configure('Vertical.TScrollbar', background='#CBD5E1', troughcolor=Theme.SURFACE,
                    bordercolor=Theme.SURFACE, arrowcolor=Theme.MUTED, relief='flat')
    style.configure('Horizontal.TScrollbar', background='#CBD5E1', troughcolor=Theme.SURFACE,
                    bordercolor=Theme.SURFACE, arrowcolor=Theme.MUTED, relief='flat')

    # ---------- 状态栏 ----------
    style.configure('Status.TLabel', background='#E8ECF3', foreground=Theme.TEXT_SUB,
                    padding=(10, 5), font=(F, 9))

    root.configure(bg=Theme.BG)
    return style


# ================================================================================
# 自绘 UI 组件：圆角矩形 / 品牌头部 / 版块标题（纯 tkinter Canvas 实现）
# ================================================================================
def round_rect(canvas, x1, y1, x2, y2, r=10, **kwargs):
    """在 Canvas 上绘制圆角矩形（用多边形平滑模拟），返回图形 id。"""
    points = [
        x1 + r, y1, x2 - r, y1,
        x2, y1, x2, y1 + r,
        x2, y2 - r, x2, y2,
        x2 - r, y2, x1 + r, y2,
        x1, y2, x1, y2 - r,
        x1, y1 + r, x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)


class BrandHeader(tk.Frame):
    """顶部品牌栏：左侧圆角图标 + 标题/副标题，右侧版本与装饰。"""

    def __init__(self, parent):
        super().__init__(parent, bg=Theme.HEADER_BG, height=84)
        self.pack(fill='x', side='top')
        self.pack_propagate(False)

        c = tk.Canvas(self, bg=Theme.HEADER_BG, highlightthickness=0, height=84)
        c.pack(fill='both', expand=True)
        self.canvas = c

        # 静态元素：左侧图标 + 标题 + 副标题
        round_rect(c, 18, 18, 66, 66, r=12, fill=Theme.PRIMARY_MID, outline='')
        c.create_polygon([32, 28, 50, 28, 54, 32, 54, 56, 32, 56],
                         outline='#FFFFFF', width=2, fill='')
        c.create_line([36, 36, 50, 36], fill='#C7D2FE', width=2)
        c.create_line([36, 41, 48, 41], fill='#C7D2FE', width=2)
        c.create_line([36, 46, 46, 46], fill='#C7D2FE', width=2)
        c.create_text(82, 32, anchor='w', text='文件批量重命名工具',
                      fill='#FFFFFF', font=(Theme.FONT, 17, 'bold'))
        c.create_text(83, 56, anchor='w',
                      text='批量处理  ·  实时预览  ·  安全撤销',
                      fill=Theme.HEADER_ACCENT, font=(Theme.FONT, 10))

        # 右侧版本徽标 + 底部高光线：随宽度变化重绘（先给合法初始坐标）
        self._badge = c.create_polygon([0, 0, 0, 0, 0, 0, 0, 0], fill='#4B45A6', outline='')
        self._badge_text = c.create_text(0, 0, text='')
        self._divider = c.create_line(0, 82, 0, 82, fill='#4B45A6', width=2)
        c.bind('<Configure>', self._on_resize)

    def _on_resize(self, event):
        """头部宽度变化时，把版本徽标贴到右侧、重画底部分隔线。"""
        c = self.canvas
        w = event.width
        bx2 = w - 18
        bx1 = bx2 - 110
        c.coords(self._badge, bx1, 30, bx2, 30, bx2, 54, bx1, 54)
        c.coords(self._badge_text, (bx1 + bx2) // 2, 42)
        c.itemconfig(self._badge_text, text='v1.0  ·  LOCAL',
                     fill='#C7D2FE', font=(Theme.FONT, 9, 'bold'))
        c.coords(self._divider, 0, 82, w, 82)


def add_section_title(parent, text, row=0, column=0, **grid_kw):
    """在给定父容器中添加带强调色竖条的版块标题，返回所在 Frame。"""
    bar = ttk.Frame(parent, style='Card.TFrame')
    bar.grid(row=row, column=column, sticky='w', **grid_kw)
    accent = tk.Frame(bar, bg=Theme.PRIMARY, width=4, height=16)
    accent.pack(side='left', padx=(0, 8), pady=2)
    accent.pack_propagate(False)
    ttk.Label(bar, text=text, style='Section.TLabel').pack(side='left')
    return bar


# ================================================================================
# 弹窗通用样式工具
# ================================================================================
def dialog_header(dlg, title, subtitle=None, color=None):
    """为弹窗添加统一风格的顶部标题条，返回该 Frame。"""
    color = color or Theme.PRIMARY
    bar = tk.Frame(dlg, bg=color, height=54)
    bar.pack(fill='x')
    bar.pack_propagate(False)
    tk.Label(bar, text='  ' + title, bg=color, fg='#FFFFFF',
             font=(Theme.FONT, 12, 'bold')).pack(anchor='w', pady=(8, 0))
    if subtitle:
        tk.Label(bar, text='  ' + subtitle, bg=color, fg='#E0E7FF',
                 font=(Theme.FONT, 9)).pack(anchor='w')
    return bar


def center_dialog(dlg, parent):
    """将弹窗居中于父窗口所在屏幕。"""
    dlg.update_idletasks()
    w, h = dlg.winfo_width(), dlg.winfo_height()
    sw, sh = parent.winfo_screenwidth(), parent.winfo_screenheight()
    dlg.geometry(f'+{(sw - w) // 2}+{(sh - h) // 2}')

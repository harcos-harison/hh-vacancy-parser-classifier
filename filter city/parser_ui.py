# -*- coding: utf-8 -*-
"""
Интерфейс для парсера HH: выбор языка, ввод параметров, отображение вакансий.
Главный файл save_csv_2.py не изменяется — все вызовы через import.
"""

import os
import sys

# Рабочая папка = папка скрипта (чтобы импорт save_csv_2 и экспорт работали при запуске из любой директории)
_script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_script_dir)
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, font as tkfont
import threading
from save_csv_2 import get_all_vacancies, save_vacancies_to_xlsx

# --- Тексты по языкам ---
TEXTS = {
    "ru": {
        "title": "Парсер вакансий HH.ru",
        "lang_label": "Язык",
        "city_label": "Город",
        "query_label": "Ключевое слово",
        "search_btn": "Искать вакансии",
        "export_btn": "Экспорт в Excel",
        "loading": "Загрузка...",
        "found": "Найдено: {} вакансий",
        "no_results": "Вакансии не найдены",
        "error_region": "Регион для города «{}» не найден",
        "vacancy": "Вакансия",
        "company": "Компания",
        "city": "Город",
        "salary": "Зарплата",
        "link": "Ссылка",
        "description": "Описание",
        "close": "Закрыть",
        "export_ok": "Сохранено: {}",
        "fill_fields": "Укажите город и ключевое слово",
    },
    "en": {
        "title": "HH.ru Vacancy Parser",
        "lang_label": "Language",
        "city_label": "City",
        "query_label": "Keyword",
        "search_btn": "Search vacancies",
        "export_btn": "Export to Excel",
        "loading": "Loading...",
        "found": "Found: {} vacancies",
        "no_results": "No vacancies found",
        "error_region": "Region for city «{}» not found",
        "vacancy": "Vacancy",
        "company": "Company",
        "city": "City",
        "salary": "Salary",
        "link": "Link",
        "description": "Description",
        "close": "Close",
        "export_ok": "Saved: {}",
        "fill_fields": "Enter city and keyword",
    },
}

# Тёмная палитра
COLORS = {
    "bg": "#1a1b26",
    "card": "#24283b",
    "accent": "#7aa2f7",
    "accent_hover": "#89b4fa",
    "text": "#c0caf5",
    "text_dim": "#a9b1d6",
    "border": "#414868",
    "success": "#9ece6a",
    "error": "#f7768e",
}


def format_salary(v):
    """Форматирование зарплаты для отображения."""
    if not v:
        return ""
    salary_from = v.get("salary_from")
    salary_to = v.get("salary_to")
    currency = v.get("currency") or ""
    if salary_from and salary_to:
        return f"{salary_from} – {salary_to} {currency}"
    if salary_from:
        return f"от {salary_from} {currency}"
    if salary_to:
        return f"до {salary_to} {currency}"
    return "—"


class ParserUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(TEXTS["ru"]["title"])
        self.root.geometry("960x640")
        self.root.configure(bg=COLORS["bg"])
        self.root.minsize(720, 480)

        self.lang = tk.StringVar(value="ru")
        self.vacancies = []
        self._build_ui()
        self._apply_theme()

    def _(self, key):
        return TEXTS[self.lang.get()].get(key, key)

    def _apply_theme(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "TFrame",
            background=COLORS["bg"],
        )
        style.configure(
            "TLabel",
            background=COLORS["bg"],
            foreground=COLORS["text"],
            font=("Segoe UI", 10),
        )
        style.configure(
            "TButton",
            background=COLORS["accent"],
            foreground=COLORS["bg"],
            font=("Segoe UI", 10),
            padding=(12, 6),
        )
        style.map("TButton", background=[("active", COLORS["accent_hover"])])
        style.configure(
            "TEntry",
            fieldbackground=COLORS["card"],
            foreground=COLORS["text"],
            insertcolor=COLORS["text"],
            padding=6,
        )
        style.configure(
            "TCombobox",
            fieldbackground=COLORS["card"],
            background=COLORS["card"],
            foreground=COLORS["text"],
            arrowcolor=COLORS["text"],
            padding=6,
        )
        style.configure(
            "Treeview",
            background=COLORS["card"],
            foreground=COLORS["text"],
            fieldbackground=COLORS["card"],
            borderwidth=0,
            rowheight=28,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["border"],
            foreground=COLORS["text"],
            font=("Segoe UI", 9, "bold"),
        )
        style.map("Treeview", background=[("selected", COLORS["accent"])])

    def _build_ui(self):
        # Верхняя панель: язык и поля ввода
        top = ttk.Frame(self.root, padding=16)
        top.pack(fill=tk.X)

        lang_frame = ttk.Frame(top)
        lang_frame.pack(side=tk.LEFT, padx=(0, 24))
        ttk.Label(lang_frame, text=self._("lang_label") + ":").pack(side=tk.LEFT, padx=(0, 8))
        lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.lang,
            values=["ru", "en"],
            state="readonly",
            width=6,
        )
        lang_combo.pack(side=tk.LEFT)
        lang_combo.bind("<<ComboboxSelected>>", self._on_lang_change)

        ttk.Label(top, text=self._("city_label") + ":").pack(side=tk.LEFT, padx=(0, 8))
        self.city_var = tk.StringVar()
        self.city_entry = ttk.Entry(top, textvariable=self.city_var, width=20)
        self.city_entry.pack(side=tk.LEFT, padx=(0, 16))

        ttk.Label(top, text=self._("query_label") + ":").pack(side=tk.LEFT, padx=(0, 8))
        self.query_var = tk.StringVar()
        self.query_entry = ttk.Entry(top, textvariable=self.query_var, width=28)
        self.query_entry.pack(side=tk.LEFT, padx=(0, 12))

        self.search_btn = ttk.Button(top, text=self._("search_btn"), command=self._on_search)
        self.search_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.export_btn = ttk.Button(top, text=self._("export_btn"), command=self._on_export, state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT)

        # Статус
        self.status_var = tk.StringVar(value="")
        status_label = ttk.Label(top, textvariable=self.status_var, foreground=COLORS["text_dim"])
        status_label.pack(side=tk.RIGHT)

        # Таблица результатов
        table_frame = ttk.Frame(self.root, padding=(16, 0, 16, 16))
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "company", "city", "salary", "url")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=16,
            selectmode="browse",
        )
        self.tree.heading("name", text=self._("vacancy"))
        self.tree.heading("company", text=self._("company"))
        self.tree.heading("city", text=self._("city"))
        self.tree.heading("salary", text=self._("salary"))
        self.tree.heading("url", text=self._("link"))

        self.tree.column("name", width=220, minwidth=120)
        self.tree.column("company", width=180, minwidth=100)
        self.tree.column("city", width=100, minwidth=80)
        self.tree.column("salary", width=140, minwidth=80)
        self.tree.column("url", width=280, minwidth=150)

        scroll_y = ttk.Scrollbar(table_frame)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.configure(command=self.tree.yview)
        scroll_x.configure(command=self.tree.xview)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.bind("<Double-1>", self._on_row_double_click)

    def _on_lang_change(self, event=None):
        self.root.title(self._("title"))
        self.search_btn.configure(text=self._("search_btn"))
        self.export_btn.configure(text=self._("export_btn"))
        for cid, key in [("name", "vacancy"), ("company", "company"), ("city", "city"), ("salary", "salary"), ("url", "link")]:
            self.tree.heading(cid, text=self._(key))

    def _on_search(self):
        city = self.city_var.get().strip()
        query = self.query_var.get().strip()
        if not city or not query:
            messagebox.showwarning(self._("title"), self._("fill_fields"))
            return

        self.search_btn.configure(state=tk.DISABLED)
        self.status_var.set(self._("loading"))
        self.export_btn.configure(state=tk.DISABLED)
        for item in self.tree.get_children():
            self.tree.delete(item)

        def run():
            try:
                vacs = get_all_vacancies(text=query, city_name=city, per_page=20)
                self.root.after(0, lambda: self._show_results(vacs, city))
            except Exception as e:
                self.root.after(0, lambda: self._show_error(str(e)))

        threading.Thread(target=run, daemon=True).start()

    def _show_results(self, vacancies, city):
        self.vacancies = vacancies
        self.search_btn.configure(state=tk.NORMAL)
        self.export_btn.configure(state=tk.NORMAL if vacancies else tk.DISABLED)

        if not vacancies:
            self.status_var.set(self._("no_results"))
            return

        self.status_var.set(self._("found").format(len(vacancies)))
        for i, v in enumerate(vacancies):
            salary_str = format_salary(v)
            url_short = (v.get("url") or "")[:50] + ("..." if len(v.get("url") or "") > 50 else "")
            self.tree.insert("", tk.END, iid=str(i), values=(
                (v.get("name") or "")[:60],
                (v.get("company") or "")[:40],
                v.get("city") or "",
                salary_str[:30],
                url_short,
            ))

    def _show_error(self, msg):
        self.search_btn.configure(state=tk.NORMAL)
        self.status_var.set("")
        messagebox.showerror(self._("title"), msg)

    def _on_row_double_click(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        iid = sel[0]
        try:
            idx = int(iid)
        except (ValueError, TypeError):
            return
        if 0 <= idx < len(self.vacancies):
            self._show_detail(self.vacancies[idx])

    def _show_detail(self, v):
        win = tk.Toplevel(self.root)
        win.title((v.get("name") or "Вакансия")[:60])
        win.geometry("560x420")
        win.configure(bg=COLORS["bg"])
        win.minsize(400, 300)

        # Контент в тёмном фоне
        main = tk.Frame(win, bg=COLORS["bg"], padx=16, pady=16)
        main.pack(fill=tk.BOTH, expand=True)

        def line(key, label_key, value):
            f = tk.Frame(main, bg=COLORS["bg"])
            f.pack(fill=tk.X, pady=4)
            tk.Label(f, text=self._(label_key) + ":", bg=COLORS["bg"], fg=COLORS["text_dim"], font=("Segoe UI", 9)).pack(side=tk.LEFT, anchor=tk.W)
            tk.Label(f, text=value or "—", bg=COLORS["bg"], fg=COLORS["text"], font=("Segoe UI", 10), wraplength=480, justify=tk.LEFT).pack(side=tk.LEFT, fill=tk.X, expand=True, anchor=tk.W)

        line("name", "vacancy", v.get("name"))
        line("company", "company", v.get("company"))
        line("city", "city", v.get("city"))
        line("salary", "salary", format_salary(v))
        line("link", "link", v.get("url"))

        tk.Label(main, text=self._("description") + ":", bg=COLORS["bg"], fg=COLORS["text_dim"], font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(12, 4))
        desc_text = scrolledtext.ScrolledText(
            main,
            wrap=tk.WORD,
            height=12,
            bg=COLORS["card"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            relief=tk.FLAT,
            padx=10,
            pady=10,
            font=("Segoe UI", 9),
        )
        desc_text.pack(fill=tk.BOTH, expand=True)
        desc_text.insert(tk.END, v.get("description") or "—")
        desc_text.configure(state=tk.DISABLED)

        ttk.Button(main, text=self._("close"), command=win.destroy).pack(pady=(12, 0))

    def _on_export(self):
        if not self.vacancies:
            return
        city = self.city_var.get().strip() or "vacancies"
        filename = f"vacancies_{city}.xlsx"
        try:
            save_vacancies_to_xlsx(self.vacancies, filename)
            messagebox.showinfo(self._("title"), self._("export_ok").format(filename))
        except Exception as e:
            messagebox.showerror(self._("title"), str(e))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ParserUI()
    app.run()

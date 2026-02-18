# -*- coding: utf-8 -*-
"""
Веб-интерфейс для парсера HH.ru.
Использует save_csv_2.py без изменений.
"""

import os
import io
import uuid
import json
import threading
from flask import Flask, render_template, request, send_file, redirect, url_for, jsonify

# рабочая папка = папка этого файла (для импорта save_csv_2)
_app_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_app_dir)
import sys
if _app_dir not in sys.path:
    sys.path.insert(0, _app_dir)

from save_csv_2 import (
    get_all_vacancies,
    get_area_id_by_city,
    get_vacancies_by_region,
    parse_vacancies,
)  # save_csv_2 не изменяем
import pandas as pd

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "hh-parser-dev-key")
app.vacancy_cache = {}
app.search_progress = {}
app.search_results = {}
MAX_CACHE_ENTRIES = 20

TEXTS = {
    "ru": {
        "title": "Парсер вакансий HH.ru",
        "lang_label": "Язык",
        "city_label": "Город",
        "query_label": "Ключевое слово",
        "search_btn": "Искать вакансии",
        "export_btn": "Скачать Excel",
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
        "fill_fields": "Укажите город и ключевое слово",
        "details": "Подробнее",
        "fast_search": "Быстрый поиск (без полных описаний)",
        "tab_results": "Результаты",
        "tab_analytics": "Аналитика",
        "progress_page": "Страница {} из {}",
        "progress_full": "Загрузка описаний...",
        "by_direction": "По направлениям",
        "by_technology": "Технологии",
        "top_companies": "Топ компаний",
        "salary_dist": "Зарплаты (от)",
    },
    "en": {
        "title": "HH.ru Vacancy Parser",
        "lang_label": "Language",
        "city_label": "City",
        "query_label": "Keyword",
        "search_btn": "Search vacancies",
        "export_btn": "Download Excel",
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
        "fill_fields": "Enter city and keyword",
        "details": "Details",
        "fast_search": "Fast search (no full descriptions)",
        "tab_results": "Results",
        "tab_analytics": "Analytics",
        "progress_page": "Page {} of {}",
        "progress_full": "Loading descriptions...",
        "by_direction": "By direction",
        "by_technology": "Technologies",
        "top_companies": "Top companies",
        "salary_dist": "Salary (from)",
    },
}


# Направления и технологии для аналитики (ключевые слова, по которым считаем вхождения)
DIRECTION_KEYWORDS = {
    "Backend": ["backend", "бэкенд", "бэкенд", "back-end", "серверн"],
    "Frontend": ["frontend", "фронтенд", "front-end", "front end", "верстк", "верстальщик"],
    "Fullstack": ["fullstack", "full-stack", "фуллстек", "full stack"],
    "Data / ML": ["data science", "machine learning", "ml", "аналитик данных", "data analyst", "нейросет", "ai ", "искусственный интеллект"],
    "DevOps / SRE": ["devops", "sre", "инфраструктур", "ci/cd", "deployment"],
    "Mobile": ["mobile", "мобильн", "android", "ios", "react native", "flutter", "кроссплатформен"],
    "QA / Тестирование": ["qa", "тестиров", "quality assurance", "automation test", "sdet"],
    "Управление": ["менеджер", "manager", "team lead", "тимлид", "руководитель", "project manager", "pm "],
}

TECH_KEYWORDS = [
    "Python", "Java", "JavaScript", "TypeScript", "React", "Vue", "Angular",
    "SQL", "PostgreSQL", "MongoDB", "Redis", "Docker", "Kubernetes", "K8s",
    "Git", "Linux", "AWS", "Kotlin", "Swift", "Go", "Golang", "PHP", "C#",
    "1C", "Node.js", "Django", "Flask", "FastAPI", "Spring", "GraphQL", "REST",
]


def get_vacancies_fast(text, city_name, per_page=20, max_pages=10, progress_callback=None):
    """Быстрый поиск с опциональным отчётом прогресса."""
    area_id = get_area_id_by_city(city_name)
    if not area_id:
        return []
    all_vacancies = []
    page = 0
    while page < max_pages:
        if progress_callback:
            progress_callback(page + 1, max_pages, "page")
        data = get_vacancies_by_region(text=text, area_id=area_id, per_page=per_page, page=page)
        vacancies = parse_vacancies(data)
        vacancies = [v for v in vacancies if v["city"].lower() == city_name.lower()]
        if not vacancies:
            break
        all_vacancies.extend(vacancies)
        page += 1
    return all_vacancies


def _count_keywords(text, keywords):
    if not text:
        return 0
    t = text.lower()
    return sum(1 for kw in keywords if kw.lower() in t)


def compute_analytics(vacancies):
    """Классификация по направлениям, технологиям, топ компаний, зарплаты."""
    by_direction = {name: 0 for name in DIRECTION_KEYWORDS}
    by_technology = {tech: 0 for tech in TECH_KEYWORDS}
    company_count = {}
    salary_values = []

    for v in vacancies:
        name = (v.get("name") or "")
        desc = (v.get("description") or "")
        combined = name + " " + desc

        for direction, keywords in DIRECTION_KEYWORDS.items():
            if _count_keywords(combined, keywords) > 0:
                by_direction[direction] += 1

        for tech in TECH_KEYWORDS:
            if tech.lower() in combined.lower():
                by_technology[tech] += 1

        company = (v.get("company") or "").strip()
        if company:
            company_count[company] = company_count.get(company, 0) + 1

        sal = v.get("salary_from")
        if sal is not None and isinstance(sal, (int, float)):
            salary_values.append(sal)

    by_direction = {k: v for k, v in by_direction.items() if v > 0}
    by_technology = {k: v for k, v in by_technology.items() if v > 0}
    top_companies = sorted(company_count.items(), key=lambda x: -x[1])[:15]

    salary_bins = {}
    if salary_values:
        for s in salary_values:
            if s < 50000:
                key = "до 50k"
            elif s < 100000:
                key = "50–100k"
            elif s < 150000:
                key = "100–150k"
            elif s < 200000:
                key = "150–200k"
            elif s < 300000:
                key = "200–300k"
            else:
                key = "300k+"
            salary_bins[key] = salary_bins.get(key, 0) + 1
    salary_order = ["до 50k", "50–100k", "100–150k", "150–200k", "200–300k", "300k+"]
    salary_dist = {k: salary_bins.get(k, 0) for k in salary_order if salary_bins.get(k, 0) > 0}

    return {
        "by_direction": by_direction,
        "by_technology": by_technology,
        "top_companies": top_companies,
        "salary_dist": salary_dist,
    }


def format_salary(v):
    if not v:
        return "—"
    a, b, c = v.get("salary_from"), v.get("salary_to"), v.get("currency") or ""
    if a and b:
        return f"{a} – {b} {c}"
    if a:
        return f"от {a} {c}"
    if b:
        return f"до {b} {c}"
    return "—"


def _run_search(search_id, city, query, fast, lang):
    t = TEXTS.get(lang, TEXTS["ru"])
    try:
        if fast:
            def progress(current, total, kind):
                pct = int(100 * current / total) if total else 0
                msg = t["progress_page"].format(current, total)
                app.search_progress[search_id] = {"status": "running", "progress": min(pct, 99), "message": msg}
                print(f"\r[{search_id[:8]}] {msg} ({pct}%)", end="", flush=True)

            print(f"\n[{search_id[:8]}] Старт быстрого поиска: {query} @ {city}")
            vacancies = get_vacancies_fast(text=query, city_name=city, per_page=20, max_pages=10, progress_callback=progress)
            print(f"\n[{search_id[:8]}] Готово: {len(vacancies)} вакансий")
        else:
            app.search_progress[search_id] = {"status": "running", "progress": 0, "message": t["progress_full"]}
            print(f"\n[{search_id[:8]}] Старт полного поиска: {query} @ {city} (это займёт время)")
            vacancies = get_all_vacancies(text=query, city_name=city, per_page=20, max_pages=10)
            print(f"\n[{search_id[:8]}] Готово: {len(vacancies)} вакансий")

        for v in vacancies:
            v["salary_str"] = format_salary(v)

        cache_key = None
        if vacancies:
            cache_key = str(uuid.uuid4())
            while len(app.vacancy_cache) >= MAX_CACHE_ENTRIES:
                app.vacancy_cache.pop(next(iter(app.vacancy_cache)))
            app.vacancy_cache[cache_key] = [dict(v) for v in vacancies]

        analytics = compute_analytics(vacancies)
        app.search_progress[search_id] = {"status": "done", "progress": 100, "message": ""}
        app.search_results[search_id] = {
            "vacancies": vacancies,
            "vacancies_json": json.dumps(vacancies, ensure_ascii=False),
            "cache_key": cache_key,
            "city": city,
            "query": query,
            "count": len(vacancies),
            "found_msg": t["found"].format(len(vacancies)),
            "analytics": analytics,
            "texts": {k: t.get(k, "") for k in ["vacancy", "company", "city", "salary", "link", "details", "tab_results", "tab_analytics", "by_direction", "by_technology", "top_companies", "salary_dist"]},
        }
    except Exception as e:
        app.search_progress[search_id] = {"status": "error", "progress": 0, "message": str(e)}
        print(f"\n[{search_id[:8]}] Ошибка: {e}")


def _get_search_params():
    """Читает city, query, lang, fast из JSON или form."""
    data = None
    if request.is_json or (request.get_data() and request.get_data().strip()):
        try:
            data = request.get_json(silent=True)
            if data is None and request.get_data():
                data = json.loads(request.get_data().as_text())
        except Exception:
            pass
    if not data:
        data = request.form
    city = (data.get("city") or "").strip()
    query = (data.get("query") or "").strip()
    lang = (data.get("lang") or "ru").strip() or "ru"
    fast = data.get("fast") in (True, "1", "true", "on")
    return city, query, lang, fast


@app.route("/", methods=["GET", "POST"])
def index():
    lang = request.args.get("lang", "ru") or request.form.get("lang", "ru") or "ru"
    if lang not in TEXTS:
        lang = "ru"
    t = TEXTS[lang]

    # Синхронный поиск (форма без JS или запасной вариант)
    if request.method == "POST" and request.form.get("city"):
        city = (request.form.get("city") or "").strip()
        query = (request.form.get("query") or "").strip()
        lang = request.form.get("lang", "ru") or "ru"
        fast = request.form.get("fast") == "1"
        if not city or not query:
            return render_template("index.html", lang=lang, texts=TEXTS[lang], error=t["fill_fields"], city=city, query=query)
        try:
            if fast:
                vacancies = get_vacancies_fast(text=query, city_name=city, per_page=20, max_pages=10)
            else:
                vacancies = get_all_vacancies(text=query, city_name=city, per_page=20, max_pages=10)
        except Exception as e:
            return render_template("index.html", lang=lang, texts=TEXTS[lang], error=str(e), city=city, query=query)
        for v in vacancies:
            v["salary_str"] = format_salary(v)
        cache_key = str(uuid.uuid4()) if vacancies else None
        if vacancies:
            while len(app.vacancy_cache) >= MAX_CACHE_ENTRIES:
                app.vacancy_cache.pop(next(iter(app.vacancy_cache)))
            app.vacancy_cache[cache_key] = [dict(v) for v in vacancies]
        analytics = compute_analytics(vacancies)
        vacancies_json = json.dumps(vacancies, ensure_ascii=False) if vacancies else "[]"
        return render_template(
            "index.html",
            lang=lang,
            texts=TEXTS[lang],
            vacancies=vacancies,
            vacancies_json=vacancies_json,
            city=city,
            query=query,
            count=len(vacancies),
            found_msg=t["found"].format(len(vacancies)),
            cache_key=cache_key,
            analytics=analytics,
        )

    return render_template("index.html", lang=lang, texts=TEXTS[lang])


@app.route("/search", methods=["POST"])
def search_start():
    city, query, lang, fast = _get_search_params()
    t = TEXTS.get(lang, TEXTS["ru"])
    if not city or not query:
        return jsonify({"error": t["fill_fields"]}), 400

    search_id = str(uuid.uuid4())
    app.search_progress[search_id] = {"status": "running", "progress": 0, "message": t["loading"]}
    thread = threading.Thread(target=_run_search, args=(search_id, city, query, fast, lang), daemon=True)
    thread.start()
    return jsonify({"search_id": search_id})


@app.route("/search_status/<search_id>")
def search_status(search_id):
    data = app.search_progress.get(search_id, {"status": "unknown", "progress": 0, "message": ""})
    return jsonify(data)


@app.route("/search_result/<search_id>")
def search_result(search_id):
    data = app.search_results.pop(search_id, None)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data)


@app.route("/export")
def export():
    key = request.args.get("key", "").strip()
    vacancies = app.vacancy_cache.pop(key, None) if key else None
    if not vacancies:
        return redirect(url_for("index"))

    df = pd.DataFrame(vacancies)
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    buf.seek(0)
    city = (vacancies[0].get("city") or "vacancies").strip()
    filename = f"vacancies_{city}.xlsx"
    return send_file(
        buf,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

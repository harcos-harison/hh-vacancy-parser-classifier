import streamlit as st
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
from io import BytesIO

# =========================================================
# 1. ТВОЯ КЛАССИФИКАЦИЯ (СЛОВАРЬ И ЛОГИКА ПРИОРИТЕТОВ)
# =========================================================
CATEGORIES = {
    # 1. ТЕСТИРОВАНИЕ (QA) - самая большая группа из твоего списка
    "QA & Automation": [
        "qa", "тест", "автотест", "тестировщик", "automation", "испытания",
        "нагрузочному тестированию", "нагрузочное", "manual", "selenium", "apium"
    ],

    # 2. КИБЕРБЕЗОПАСНОСТЬ И РЕВЕРС
    "Cybersecurity": [
        "пентестер", "pentest", "security", "безопасность", "reverse", "реверс", 
        "appsec", "soc", "siem", "кибер", "доступов", "мониторинг"
    ],

    # 3. ИСКУССТВЕННЫЙ ИНТЕЛЛЕКТ И ДАННЫЕ
    "AI & Data": [
        "llm", "искусственный интеллект", "ai", "ml", "prompt", "промпт",
        "data analyst", "аналитик данных", "bi", "sql", "нейросети", "computer vision"
    ],

    # 4. СИСТЕМНОЕ И СЕТЕВОЕ ИНЖЕНЕРСТВО
    "System & Network": [
        "системный инженер", "kubernetes", "k8s", "voip", "asterisk", "сетевой",
        "системный администратор", "sysadmin", "linux", "sre", "devops"
    ],

    # 5. ИНЖЕНЕРИЯ И АСУ ТП (ПРОМЫШЛЕННОСТЬ)
    "Industrial Engineering": [
        "асу тп", "электроник", "электронщик", "радиоэлектрон", "плис", 
        "fpga", "автоматизации", "dsp", "sdr"
    ],

    # 6. IT-HR И ОБУЧЕНИЕ
    "HR & Education": [
        "рекрутер", "recruiter", "обучению", "развитию", "преподаватель", 
        "учитель", "методист", "наставник"
    ],

    # 7. РАЗРАБОТКА (Backend, Frontend, Fullstack)
    "Development": [
        "разработчик", "developer", "программист", "backend", "frontend", 
        "fullstack", "gamedev", "python", "java", "c#", ".net"
    ],

    # 8. ПОДДЕРЖКА И АНАЛИЗ (БИЗНЕС)
    "Support & Analysis": [
        "поддержк", "helpdesk", "технический ассистент", "системный аналитик", 
        "бизнес-аналитик", "product", "project", "менеджер"
    ]
}

# Приоритет: QA ставим выше Development, чтобы "QA Python Engineer" попал в QA, а не в Dev.
PRIORITY = [
    "QA & Automation", "Cybersecurity", "AI & Data", "System & Network",
    "Industrial Engineering", "HR & Education", "Development", "Support & Analysis"
]

def classify_title(title):
    # Очищаем название от тире и слешей, чтобы "QA-инженер" стал "QA инженер"
    title = str(title).lower().replace('-', ' ').replace('/', ' ').strip()

    scores = {cat: 0 for cat in CATEGORIES}

    for category in PRIORITY:
        for keyword in CATEGORIES[category]:
            # Ищем ключевое слово как подстроку
            if keyword.lower() in title:
                # Если нашли прямое попадание (например, "пентестер"), 
                # даем этой категории большой вес
                scores[category] += 5 
    
    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return "Other"

    return best_category

# =========================================================
# 2. ФУНКЦИИ ПАРСИНГА (HH.RU API + BS4)
# =========================================================
@st.cache_data
def get_area_id_by_city(city_name):
    try:
        res = requests.get("https://api.hh.ru/areas")
        areas = res.json()
        def search(areas_list):
            for a in areas_list:
                if a["name"].lower() == city_name.lower(): return a["id"]
                if a.get("areas"):
                    r = search(a["areas"])
                    if r: return r
            return None
        return search(areas)
    except: return None

def fetch_full_description(url):
    try:
        r = requests.get(url, headers={"User-Agent": "HH-Parser/1.0"}, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        block = soup.find("div", {"data-qa": "vacancy-description"}) or soup.find("div", class_="g-user-content")
        return block.get_text(separator="\n").strip() if block else ""
    except: return ""

def start_parsing(text, city_name, max_pages):
    area_id = get_area_id_by_city(city_name)
    if not area_id: return None, "Город не найден"

    all_vacancies = []
    status_container = st.empty() 
    progress_bar = st.progress(0)

    for page in range(max_pages):
        params = {"text": text, "area": area_id, "per_page": 20, "page": page}
        res = requests.get("https://api.hh.ru/vacancies", params=params)
        if res.status_code != 200: break
        
        items = res.json().get("items", [])
        if not items: break

        for item in items:
            name = item.get("name")
            url = item.get("alternate_url")
            status_container.info(f"⏳ Парсим: {name[:40]}...")
            
            desc = fetch_full_description(url)
            salary = item.get("salary")
            
            all_vacancies.append({
                "name": name,
                "category": classify_title(name),
                "company": item.get("employer", {}).get("name"),
                "city": city_name,
                "salary_from": salary["from"] if salary else None,
                "salary_to": salary["to"] if salary else None,
                "currency": salary["currency"] if salary else None,
                "experience": item.get("experience", {}).get("name", "Не указан"),
                "url": url,
                "description": desc
            })
            time.sleep(0.1) 
        
        progress_bar.progress((page + 1) / max_pages)
    
    status_container.success("✅ Парсинг завершен!")
    return pd.DataFrame(all_vacancies), None

# =========================================================
# 3. ИНТЕРФЕЙС STREAMLIT
# =========================================================
st.header("🔎 Сбор и классификация вакансий")

# Инициализируем сессию для данных и для фильтра
if 'vacancies_df' not in st.session_state:
    st.session_state['vacancies_df'] = None
if 'selected_category' not in st.session_state:
    st.session_state['selected_category'] = "Все"

# Форма настроек
with st.form("parser_settings"):
    col1, col2 = st.columns(2)
    city_in = col1.text_input("Введите город", value="Уфа")
    query_in = col2.text_input("Ключевое слово", value="Python")
    limit_in = st.slider("Сколько страниц искать?", 1, 10, 2)
    submit = st.form_submit_button("Запустить процесс")

if submit:
    df_result, err = start_parsing(query_in, city_in, limit_in)
    if err:
        st.error(err)
    else:
        st.session_state['vacancies_df'] = df_result
        st.session_state['selected_category'] = "Все" # Сброс фильтра при новом поиске

# ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ
if st.session_state['vacancies_df'] is not None:
    df = st.session_state['vacancies_df']
    
    st.divider()
    st.subheader("📊 Результаты и фильтрация")
    
    # 1. Интерактивные "Метрики-кнопки"
    cat_counts = df["category"].value_counts()
    
    st.write("Кликните на категорию, чтобы отфильтровать таблицу:")
    
    # Кнопка сброса
    if st.button("🔄 Показать все вакансии"):
        st.session_state['selected_category'] = "Все"

    # Сетка кнопок
    cols = st.columns(min(len(cat_counts), 5))
    for i, (cat, count) in enumerate(cat_counts.items()):
        if cols[i % 5].button(f"{cat}: {count}"):
            st.session_state['selected_category'] = cat

    # 2. Фильтрация данных
    if st.session_state['selected_category'] == "Все":
        display_df = df
        st.info("Сейчас показаны **все** найденные вакансии.")
    else:
        display_df = df[df["category"] == st.session_state['selected_category']]
        st.success(f"Показаны вакансии из категории: **{st.session_state['selected_category']}**")

    # 3. Таблица данных с кликабельными ссылками
    st.dataframe(
        display_df, 
        use_container_width=True,
        column_config={
            "url": st.column_config.LinkColumn("Ссылка на HH.ru")
        }
    )

    # 4. Скачивание (всегда полного файла)
    st.divider()
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 Скачать полный Excel",
        data=output.getvalue(),
        file_name=f"vacancies_{city_in}.xlsx",
        mime="application/vnd.ms-excel"
    )
    
    st.info("💡 Данные сохранены в памяти. Перейдите в раздел **Аналитика** для просмотра графиков.")
else:
    st.info("Настройте параметры выше и нажмите кнопку для начала сбора данных.")
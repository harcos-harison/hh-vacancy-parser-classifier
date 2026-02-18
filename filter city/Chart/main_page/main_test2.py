import streamlit as st
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
from io import BytesIO
from natasha import Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger, Doc

# =========================================================
# 1. НАСТРОЙКА NLP (NATASHA)
# =========================================================
segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
tagger = NewsMorphTagger(emb)

def clean_and_lemmatize(text):
    """Приводит текст к начальной форме для точного поиска."""
    if not text:
        return ""
    doc = Doc(str(text).lower().replace('-', ' ').replace('/', ' '))
    doc.segment(segmenter)
    doc.tag_morph(tagger)
    for token in doc.tokens:
        token.lemmatize(morph_vocab)
    return " ".join([_.lemma for _ in doc.tokens])

# =========================================================
# 2. РАСШИРЕННЫЙ СЛОВАРЬ КЛАССИФИКАЦИИ
# =========================================================
CATEGORIES = {
    "AI, ML & LLM": ["ai", "ml", "llm", "искусственный интеллект", "нейросеть", "vision", "cv", "prompt", "промпт", "rpa"],
    "QA & Automation": ["qa", "тест", "автотест", "тестировщик", "automation", "испытание", "manual", "selenium", "нагрузочный"],
    "Cybersecurity": ["пентестер", "pentest", "security", "безопасность", "reverse", "реверс", "appsec", "soc", "siem", "иб"],
    "Electronics & Hardware": ["электроник", "электронщик", "радиоэлектрон", "плис", "fpga", "sdr", "dsp", "схемотехник", "hardware", "embedded"],
    "Network & SysAdmin": ["сетевой", "network", "системный администратор", "sysadmin", "linux", "voip", "asterisk", "kubernetes", "k8s"],
    "Analytics & Data Science": ["аналитик", "analytics", "bi", "sql", "data scientist", "субд", "база данных", "математик"],
    "Software Development": ["разработчик", "developer", "программист", "backend", "frontend", "fullstack", "gamedev", "python", "java", "c#"],
    "Education & HR": ["преподаватель", "учитель", "методист", "наставник", "рекрутер", "recruiter", "hr", "обучение"],
    "Support & Management": ["поддержка", "helpdesk", "l2", "сопровождение", "менеджер", "product", "project", "cto", "lead"]
}

PRIORITY = ["AI, ML & LLM", "QA & Automation", "Cybersecurity", "Electronics & Hardware", 
            "Network & SysAdmin", "Analytics & Data Science", "Software Development", 
            "Education & HR", "Support & Management"]

def classify_vacancy(title, description):
    """Гибридная классификация: заголовок + описание."""
    clean_title = clean_and_lemmatize(title)
    scores = {cat: 0 for cat in CATEGORIES}

    # 1. Проверка заголовка (высокий приоритет)
    for category in PRIORITY:
        for keyword in CATEGORIES[category]:
            if keyword in clean_title:
                scores[category] += 10

    # 2. Если заголовок не дал результата, проверяем описание
    if max(scores.values()) == 0:
        clean_desc = clean_and_lemmatize(description)
        for category in PRIORITY:
            for keyword in CATEGORIES[category]:
                if keyword in clean_desc:
                    scores[category] += 1

    best_cat = max(scores, key=scores.get)
    return best_cat if scores[best_cat] > 0 else "Other"

# =========================================================
# 3. ФУНКЦИИ ПАРСИНГА
# =========================================================
@st.cache_data
def get_area_id_by_city(city_name):
    try:
        res = requests.get("https://api.hh.ru/areas")
        def search(areas_list):
            for a in areas_list:
                if a["name"].lower() == city_name.lower(): return a["id"]
                if a.get("areas"):
                    r = search(a["areas"])
                    if r: return r
            return None
        return search(res.json())
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
            status_container.info(f"⏳ Анализируем: {name[:40]}...")
            
            desc = fetch_full_description(url)
            salary = item.get("salary")
            
            all_vacancies.append({
                "name": name,
                "category": classify_vacancy(name, desc),
                "company": item.get("employer", {}).get("name"),
                "salary_from": salary["from"] if salary else None,
                "salary_to": salary["to"] if salary else None,
                "currency": salary["currency"] if salary else None,
                "experience": item.get("experience", {}).get("name", "Не указан"),
                "url": url,
                "description": desc[:] + "..." # Сохраняем часть описания
            })
            time.sleep(0.1)
        
        progress_bar.progress((page + 1) / max_pages)
    
    status_container.success("✅ Сбор и классификация завершены!")
    return pd.DataFrame(all_vacancies), None

# =========================================================
# 4. ИНТЕРФЕЙС STREAMLIT
# =========================================================
st.set_page_config(page_title="HH Smart Parser 2026", layout="wide")
st.header("🔎 Умный поиск ИТ-вакансий")

if 'vacancies_df' not in st.session_state:
    st.session_state['vacancies_df'] = None
if 'selected_cat' not in st.session_state:
    st.session_state['selected_cat'] = "Все"

with st.form("parser_settings"):
    col1, col2, col3 = st.columns([2,2,1])
    city_in = col1.text_input("Город", value="Уфа")
    query_in = col2.text_input("Ключевое слово", value="Python")
    limit_in = col3.slider("Страниц", 1, 10, 2)
    submit = st.form_submit_button("Начать сбор")

if submit:
    df_result, err = start_parsing(query_in, city_in, limit_in)
    if err: st.error(err)
    else:
        st.session_state['vacancies_df'] = df_result
        st.session_state['selected_cat'] = "Все"

if st.session_state['vacancies_df'] is not None:
    df = st.session_state['vacancies_df']
    
    # Секция фильтрации (Кнопки-Метрики)
    st.divider()
    cat_counts = df["category"].value_counts()
    st.write("### Отфильтровать по направлению:")
    
    c_all = st.columns(1)
    if c_all[0].button("🌐 Показать все вакансии"):
        st.session_state['selected_cat'] = "Все"

    cols = st.columns(min(len(cat_counts), 5))
    for i, (cat, count) in enumerate(cat_counts.items()):
        if cols[i % 5].button(f"{cat}: {count}"):
            st.session_state['selected_cat'] = cat

    # Фильтрация вывода
    display_df = df if st.session_state['selected_cat'] == "Все" else df[df["category"] == st.session_state['selected_cat']]
    
    st.success(f"Выбрано: **{st.session_state['selected_cat']}** ({len(display_df)} шт.)")
    st.dataframe(
        display_df.drop(columns=['description']), 
        use_container_width=True,
        column_config={"url": st.column_config.LinkColumn("Ссылка")}
    )

    # Скачивание
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.download_button("📥 Скачать полный Excel", output.getvalue(), f"vacancies_{city_in}.xlsx")
    st.info("💡 Теперь данные доступны в разделе **Аналитика**.")
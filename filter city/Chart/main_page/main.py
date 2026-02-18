import streamlit as st
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup
from io import BytesIO
from natasha import Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger, Doc
import re
from main_page.data import SKILL_MAP, CATEGORIES, PRIORITY
from main_page.setting.city_to_id import CITY_TO_ID

# =========================================================
# 1. НАСТРОЙКА NLP (NATASHA) И СЛОВАРЬ ТЕХНОЛОГИЙ
# =========================================================
segmenter = Segmenter()
morph_vocab = MorphVocab()
emb = NewsEmbedding()
tagger = NewsMorphTagger(emb)

# SKILL_MAP = {}

def clean_and_lemmatize(text):
    # Если текст пустой, NaN или не строка — возвращаем пустую строку
    if pd.isna(text) or not isinstance(text, str) or not text.strip():
        return ""
    
    # Теперь безопасно вызываем .lower() и замены
    clean_text = text.lower().replace('-', ' ').replace('/', ' ')
    
    doc = Doc(clean_text)
    doc.segment(segmenter)
    doc.tag_morph(tagger)
    for token in doc.tokens:
        token.lemmatize(morph_vocab)
    return " ".join([_.lemma for _ in doc.tokens])

def extract_skills(lemmatized_text):
    if not lemmatized_text: return []
    
    # Очистка текста
    text = lemmatized_text.lower()
    for char in "()/,[]": text = text.replace(char, " ")
    
    # Сюда будем сохранять найденное: { "Languages": ["python"], "Databases": ["sql"] }
    found_by_category = {cat: [] for cat in SKILL_MAP.keys()}
    
    # Собираем все навыки для поиска с привязкой к категории
    all_skills_to_search = []
    for category, skills in SKILL_MAP.items():
        for s in skills:
            all_skills_to_search.append({"name": s, "cat": category})
            
    # Сортируем по длине, чтобы сначала найти C++, а не C
    all_skills_to_search.sort(key=lambda x: len(x["name"]), reverse=True)

    for skill_item in all_skills_to_search:
        skill_clean = skill_item["name"].lower()
        
        # Паттерн (гибкий для C++ и обычный для SQL)
        if "++" in skill_clean or "#" in skill_clean:
            pattern = r"".join([re.escape(char) + r"\s*" for char in skill_clean]).strip()
        else:
            pattern = rf"\b{re.escape(skill_clean)}\b"
        
        if re.search(pattern, text):
            found_by_category[skill_item["cat"]].append(skill_item["name"])
            text = re.sub(pattern, " ", text) # Удаляем найденное из текста

    # ФОРМИРУЕМ ПРИОРИТЕТНЫЙ СПИСОК
    final_list = []
    # Идем строго по нашему порядку SKILL_ORDER
    SKILL_ORDER = ["Languages", "Frameworks", "Databases", "Infrastructure", "Tools", "Methodologies", "Security"]
    
    for category in SKILL_ORDER:
        if category in found_by_category:
            # Сортируем внутри категории по алфавиту и добавляем в общий список
            final_list.extend(sorted(found_by_category[category]))
            
    return final_list # Теперь список всегда начинается с языков

# =========================================================
# 2. УСОВЕРШЕНСТВОВАННЫЙ КЛАССИФИКАТОР
# =========================================================
# CATEGORIES = {}
# PRIORITY = []

def classify_vacancy(title, description_lemmatized):
    # Защита от NaN в заголовке
    if pd.isna(title) or not isinstance(title, str):
        title = "без названия"
        
    clean_title = clean_and_lemmatize(title)
    scores = {cat: 0 for cat in CATEGORIES}
    
    for category in PRIORITY:
        for keyword in CATEGORIES[category]:
            if keyword in clean_title: 
                scores[category] += 10
                
    if max(scores.values()) == 0:
        # Защита от NaN в описании
        desc = description_lemmatized if isinstance(description_lemmatized, str) else ""
        for category in PRIORITY:
            for keyword in CATEGORIES[category]:
                if keyword in desc: 
                    scores[category] += 1
                    
    best_cat = max(scores, key=scores.get)
    return best_cat if scores[best_cat] > 0 else "Other"

# =========================================================
# 3. ФУНКЦИИ ПАРСИНГА
# =========================================================
@st.cache_data
def get_area_id_by_city(city_name: str) -> str:
    """
    Возвращает area_id города по его названию.
    Если город не найден или пустое имя, возвращает '1' (Москва по умолчанию).
    """
    if not city_name:
        return "1"
    
    # Приводим к нижнему регистру, чтобы искать в словаре
    city_key = city_name.strip().lower()
    
    # Возвращаем ID города из словаря или '1' по умолчанию
    return CITY_TO_ID.get(city_key, "1")

"wwww"

def fetch_full_description(url):
    try:
        r = requests.get(url, headers={"User-Agent": "HH-Parser/1.0"}, timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        block = soup.find("div", {"data-qa": "vacancy-description"}) or soup.find("div", class_="g-user-content")
        return block.get_text(separator="\n").strip() if block else ""
    except: return ""

def start_parsing(text, city_name, max_pages, all_russia):
    area_id = "1" if all_russia else get_area_id_by_city(city_name)
    all_vacancies = []
    status_container = st.empty()
    progress_bar = st.progress(0)

    for page in range(max_pages):
        params = {"text": text, "area": area_id, "per_page": 20, "page": page}
        try:
            res = requests.get("https://api.hh.ru/vacancies", params=params)
            if res.status_code != 200: break
            items = res.json().get("items", [])
            if not items: break

            for item in items:
                name = item.get("name")
                url = item.get("alternate_url")
                status_container.info(f"🛰️ Регион: {'Россия' if all_russia else city_name} | Анализ: {name[:30]}...")
                
                desc = fetch_full_description(url)
                desc_lemmatized = clean_and_lemmatize(desc)
                salary = item.get("salary")
                found_skills = extract_skills(desc_lemmatized)
                
                all_vacancies.append({
                    "name": name,
                    "category": classify_vacancy(name, desc_lemmatized),
                    "company": item.get("employer", {}).get("name"),
                    "salary_from": salary["from"] if salary else None,
                    "salary_to": salary["to"] if salary else None,
                    "currency": salary["currency"] if salary else None,
                    "experience": item.get("experience", {}).get("name", "Не указан"),
                    "skills": ", ".join(found_skills),
                    "url": url,
                    "description": desc,
                    "lemmatized_content": desc_lemmatized  # НОВАЯ КОЛОНКА
                })
                time.sleep(0.05)
        except: break
        progress_bar.progress((page + 1) / max_pages)
    
    status_container.success(f"✅ Сбор завершен! Найдено {len(all_vacancies)} вакансий.")
    return pd.DataFrame(all_vacancies), None

# =========================================================
# 4. ИНТЕРФЕЙС STREAMLIT
# =========================================================
st.set_page_config(page_title="Skill Hunter 2026", layout="wide")

# Сайдбар для настроек
with st.sidebar:
    st.header("⚙️ Настройки поиска")
    all_russia = st.checkbox("🌍 Искать по всей России", value=False)
    
    if not all_russia:
        city_in = st.text_input("Город", value="Москва")
    else:
        city_in = ""
        st.info("Поиск будет выполнен по всей стране")
        
    query_in = st.text_input("Ключевое слово (Стек/Роль)", value="Python")
    limit_in = st.slider("Глубина поиска (страниц)", 1, 50, 5)
    
    st.divider()
    btn_start = st.button("🚀 Начать сбор данных", use_container_width=True)

# Основная область
st.header("🔎 Глобальный мониторинг IT-рынка")

if 'vacancies_df' not in st.session_state:
    st.session_state['vacancies_df'] = None
if 'selected_cat' not in st.session_state:
    st.session_state['selected_cat'] = "Все"

if btn_start:
    df_result, err = start_parsing(query_in, city_in, limit_in, all_russia)
    if err: st.error(err)
    else:
        st.session_state['vacancies_df'] = df_result

if st.session_state['vacancies_df'] is not None:
    df = st.session_state['vacancies_df']
    
    # Секция быстрых фильтров-кнопок
    cat_counts = df["category"].value_counts()
    st.write("### Быстрые фильтры по направлениям:")
    
    cols = st.columns(6)
    if cols[0].button("🌐 Все вакансии"): 
        st.session_state['selected_cat'] = "Все"
    
    for i, (cat, count) in enumerate(cat_counts.items()):
        if cols[(i+1) % 6].button(f"{cat}: {count}"):
            st.session_state['selected_cat'] = cat

    # Фильтрация и вывод таблицы
    display_df = df if st.session_state['selected_cat'] == "Все" else df[df["category"] == st.session_state['selected_cat']]
    
    st.info(f"Отображено: **{st.session_state['selected_cat']}** | Вакансий: **{len(display_df)}**")
    st.dataframe(
        display_df.drop(columns=['description']), 
        use_container_width=True,
        column_config={
            "url": st.column_config.LinkColumn("Ссылка"),
            "skills": st.column_config.TextColumn("Технологии", width="large")
        }
    )

    # Скачивание файла
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.download_button("📥 Скачать базу в Excel", output.getvalue(), f"hh_export_{query_in}.xlsx")
    
    
# =========================================================
# 5. УНИВЕРСАЛЬНЫЙ ОБРАБОТЧИК ФАЙЛОВ (УЛЬТРА-ЗАЩИТА)
# =========================================================
st.divider()
st.subheader("📁 Загрузка и анализ внешней базы")

up_file = st.file_uploader("Выберите Excel/CSV/JSON", type=['xlsx', 'csv', 'json'])

if up_file:
    try:
        # 1. Чтение файла
        if up_file.name.endswith('.xlsx'):
            df_file = pd.read_excel(up_file)
        elif up_file.name.endswith('.json'):
            df_file = pd.read_json(up_file)
        else:
            df_file = pd.read_csv(up_file)

        # 2. КРИТИЧЕСКАЯ ОЧИСТКА ТИПОВ ДАННЫХ
        # Переименовываем основные колонки
        name_map = {'title': 'name', 'вакансия': 'name', 'должность': 'name'}
        df_file = df_file.rename(columns=name_map)
        
        # ГАРАНТИРУЕМ, ЧТО ТЕКСТОВЫЕ КОЛОНКИ — ЭТО СТРОКИ
        # Даже если там NaN, они станут строкой "nan"
        if 'name' in df_file.columns:
            df_file['name'] = df_file['name'].astype(str).replace('nan', 'Без названия')
        else:
            df_file['name'] = "Без названия"

        if 'description' in df_file.columns:
            df_file['description'] = df_file['description'].astype(str).replace('nan', '')
        else:
            df_file['description'] = ""

        # Маппинг остальных полей
        df_file = df_file.rename(columns={'опыт': 'experience', 'опыт работы': 'experience', 'exp': 'experience'})
        if 'experience' not in df_file.columns:
            df_file['experience'] = "Не указан"
        else:
            df_file['experience'] = df_file['experience'].astype(str).replace('nan', 'Не указан')

        st.success(f"📊 Файл загружен. Строк: {len(df_file)}")

        # 3. Кнопка запуска анализа
        if st.button("🚀 Запустить полный пересчет", key="analyze_btn"):
            with st.status("🔄 Глубокий анализ 1000+ вакансий...") as status:
                
                # ЛЕММАТИЗАЦИЯ С ИНДИКАТОРОМ (важно для больших файлов)
                st.write("🧠 Работает Natasha (лемматизация)...")
                # Используем прогресс-бар для наглядности, так как 1000 строк — это долго
                df_file['lemmatized_content'] = [clean_and_lemmatize(text) for text in df_file['description']]
                
                st.write("🔍 Поиск навыков...")
                df_file['skills_list'] = df_file['lemmatized_content'].apply(extract_skills)
                df_file['skills'] = df_file['skills_list'].apply(lambda x: ", ".join(x))
                
                st.write("🗂️ Классификация ролей...")
                df_file['category'] = df_file.apply(
                    lambda row: classify_vacancy(row['name'], row['lemmatized_content']), axis=1
                )
                
                status.update(label="✅ Анализ завершен!", state="complete")

            st.session_state['vacancies_df'] = df_file
            st.rerun()

    except Exception as e:
        # Это поможет тебе увидеть, на какой именно строке или колонке ошибка
        st.error(f"⚠️ Ошибка в структуре файла: {e}")
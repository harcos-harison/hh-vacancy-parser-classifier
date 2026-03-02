import streamlit as st
import pandas as pd
import asyncio
import aiohttp
import requests
import time
import re
from bs4 import BeautifulSoup

# --- КОНФИГУРАЦИЯ ---
CITY_MAP = {
    "Москва": "1", "Санкт-Петербург": "2", "Новосибирск": "4",
    "Екатеринбург": "3", "Казань": "88", "Нижний Новгород": "66",
    "Челябинск": "104", "Самара": "78", "Омск": "68",
    "Ростов-на-Дону": "76", "Уфа": "99", "Красноярск": "54",
    "Воронеж": "26", "Пермь": "72", "Волгоград": "24", "Краснодар": "53"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}
BASE_URL = "https://api.hh.ru/vacancies"

if 'final_df' not in st.session_state:
    st.session_state['final_df'] = None

# --- ФУНКЦИИ ОЧИСТКИ ---

def clean_text_structure(html_content):
    """Превращает HTML в чистый текст с сохранением структуры блоков"""
    if not html_content: return ""
    soup = BeautifulSoup(html_content, "html.parser")
    # Используем двойной перенос как разделитель для читаемости в Excel
    text = soup.get_text(separator="  |  ")
    # Убираем лишние пробелы
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# --- АСИНХРОННЫЙ ДВИЖОК ---

async def fetch_details_stable(session, v_id, url, semaphore):
    """Стабильное получение описания: Сначала API, потом HTML-fallback"""
    async with semaphore:
        res = {"id": v_id, "full_description": "Не удалось загрузить", "key_skills": ""}
        try:
            # 1. ПЫТАЕМСЯ ЧЕРЕЗ API (Самый надежный способ для данных)
            async with session.get(f"{BASE_URL}/{v_id}", headers=HEADERS, timeout=5) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    res["key_skills"] = ", ".join([s.get('name') for s in data.get('key_skills', [])])
                    api_desc = data.get('description')
                    if api_desc:
                        res["full_description"] = clean_text_structure(api_desc)
                        return res # Если API дало текст, уходим

            # 2. FALLBACK: ПРЯМОЙ ПАРСИНГ HTML (если API вернуло пустоту или ошибку)
            async with session.get(url, headers=HEADERS, timeout=5) as resp:
                if resp.status == 200:
                    html = await resp.text()
                    soup = BeautifulSoup(html, "html.parser")
                    # Ищем именно твой блок
                    block = soup.find("div", {"data-qa": "vacancy-description"}) or \
                            soup.find("div", class_="g-user-content")
                    if block:
                        res["full_description"] = clean_text_structure(str(block))
        except:
            pass
        return res

async def run_enrichment(df):
    semaphore = asyncio.Semaphore(40) # 40 одновременных запросов - оптимально
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_details_stable(session, row['id'], row['url'], semaphore) for _, row in df.iterrows()]
        return await asyncio.gather(*tasks)

# --- БАЗОВЫЙ СБОР ---

def get_total_data(query, city_ids):
    all_vacs = []
    status = st.empty()
    
    exp_list = ["noExperience", "between1And3", "between3And6", "moreThan6"]
    
    for c_id in city_ids:
        c_name = [n for n, i in CITY_MAP.items() if i == c_id][0]
        status.info(f"🔎 Собираем список вакансий: {c_name}")
        
        for exp in exp_list:
            # Используем period=30 чтобы вытащить максимум за месяц
            for page in range(20):
                params = {"text": query, "area": c_id, "per_page": 100, "page": page, "experience": exp, "period": 30}
                try:
                    r = requests.get(BASE_URL, params=params, headers=HEADERS)
                    items = r.json().get("items", [])
                    if not items: break
                    for it in items:
                        s = it.get("salary") or {}
                        all_vacs.append({
                            "id": it.get("id"), "city": c_name, "name": it.get("name"),
                            "url": it.get("alternate_url"), "employer": it.get("employer", {}).get("name"),
                            "salary_from": s.get("from"), "experience": it.get("experience", {}).get("name")
                        })
                except: break

    df = pd.DataFrame(all_vacs).drop_duplicates(subset=['id'])
    
    # Запуск асинхронного обогащения
    status.warning(f"🚀 Глубокий парсинг описаний для {len(df)} вакансий...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    details = loop.run_until_complete(run_enrichment(df))
    
    details_df = pd.DataFrame(details)
    final = pd.merge(df, details_df, on='id', how='left')
    status.success(f"✅ Сбор завершен! Найдено: {len(final)}")
    return final

# --- UI ---
st.set_page_config(page_title="Stable HH Parser", layout="wide")
st.title("⚡ Stable Mega-Parser (16 Cities)")

q = st.text_input("Ключевое слово", "Python")
cities = st.multiselect("Города", list(CITY_MAP.keys()), default=["Москва"])

if st.button("🚀 Начать сбор"):
    ids = [CITY_MAP[c] for c in cities]
    st.session_state['final_df'] = get_total_data(q, ids)

if st.session_state['final_df'] is not None:
    data = st.session_state['final_df']
    st.dataframe(data, use_container_width=True)
    
    # Скачивание с правильной кодировкой
    csv = data.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
    st.download_button("📥 Скачать CSV для Excel", csv, "hh_stable_data.csv", "text/csv", use_container_width=True)
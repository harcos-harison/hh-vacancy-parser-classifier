import streamlit as st
import pandas as pd
import requests
import time
from transformers import pipeline

# --- 1. ЗАГРУЗКА ИИ МОДЕЛИ ---
@st.cache_resource
def load_ai_classifier():
    # Используем мультиязычную модель (BART), которая понимает русский контекст
    return pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

classifier = load_ai_classifier()

# Категории для ИИ (более точные, чтобы проверить гипотезу о разделении ролей)
AI_LABELS = [
    "Software Development", 
    "Data Science & ML", 
    "Data Engineering", 
    "System & Business Analysis", 
    "DevOps & Infrastructure", 
    "QA & Testing",
    "Cybersecurity",
    "Product & Project Management"
]

# --- 2. ФУНКЦИИ ПАРСИНГА (УПРОЩЕННЫЕ ДЛЯ ТЕСТА) ---
def fetch_test_vacancies(query, pages=1):
    url = "https://api.hh.ru/vacancies"
    params = {"text": query, "per_page": 10, "page": 0}
    try:
        res = requests.get(url, params=params)
        return res.json().get('items', [])
    except:
        return []

# --- 3. ИНТЕРФЕЙС ---
st.title("🧪 Лаборатория: Тотальный ИИ-парсинг")
st.markdown("""
На этой странице мы не используем словари. Каждую вакансию «читает» нейросеть 
**BART** и определяет её роль на основе семантики. 
*Внимание: это работает медленнее, чем основной парсер!*
""")

with st.sidebar:
    test_query = st.text_input("Поисковый запрос для теста", value="Python")
    test_limit = st.slider("Сколько вакансий проверить?", 5, 30, 10)
    start_test = st.button("🚀 Запустить ИИ-анализ")

if start_test:
    items = fetch_test_vacancies(test_query)
    
    if not items:
        st.error("Не удалось получить вакансии.")
    else:
        results = []
        progress_bar = st.progress(0)
        status = st.empty()

        for i, item in enumerate(items[:test_limit]):
            title = item.get('name')
            # Для ИИ лучше давать и заголовок, и короткое описание (snippet)
            snippet = item.get('snippet', {}).get('requirement', '')
            full_text = f"{title}. {snippet}" if snippet else title
            
            status.info(f"🤖 ИИ анализирует ({i+1}/{test_limit}): {title[:40]}...")
            
            # КЛАССИФИКАЦИЯ МОДЕЛЬЮ
            ai_result = classifier(full_text, candidate_labels=AI_LABELS)
            
            results.append({
                "Вакансия": title,
                "ИИ Категория": ai_result['labels'][0],
                "Уверенность": round(ai_result['scores'][0], 2),
                "Альтернатива": ai_result['labels'][1] # Вторая по вероятности категория
            })
            
            progress_bar.progress((i + 1) / test_limit)

        status.success("✅ Анализ завершен!")
        
        # --- 4. ВЫВОД ДАННЫХ ---
        df_ai = pd.DataFrame(results)
        
        st.subheader("📊 Результаты работы нейросети")
        st.dataframe(df_ai, use_container_width=True)

        # Аналитика распределения
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("📈 Доли категорий по мнению ИИ")
            chart_data = df_ai['ИИ Категория'].value_counts()
            st.bar_chart(chart_data)
            
        with col2:
            st.write("💡 Инсайты модели")
            low_conf = df_ai[df_ai['Уверенность'] < 0.4]
            if not low_conf.empty:
                st.warning(f"Найдено {len(low_conf)} вакансий с низкой уверенностью. Это либо 'солянка' из обязанностей, либо редкие роли.")
            else:
                st.success("Модель четко разделила все вакансии.")

        # Сравнение с "глупым" поиском
        st.divider()
        st.subheader("⚖️ Контрольное сравнение")
        
        # Возьмем одну вакансию для примера
        example = df_ai.iloc[0]
        st.write(f"Вакансия: **{example['Вакансия']}**")
        st.write(f"ИИ определил как: **{example['ИИ Категория']}** (уверенность {example['Уверенность']})")
        
        if "Analyst" in example['Вакансия'] and example['ИИ Категория'] == "Data Engineering":
            st.info("🎯 Вот он, буст! Словарный парсер назвал бы это 'Analytics', но ИИ увидел инженерные задачи.")
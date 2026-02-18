import streamlit as st
import pandas as pd
import plotly.express as px
from collections import Counter

# --- 1. ПРОВЕРКА ДАННЫХ ---
if 'vacancies_df' not in st.session_state or st.session_state['vacancies_df'] is None:
    st.warning("⚠️ Данные не найдены. Пожалуйста, сначала запустите парсер на главной странице.")
    st.stop()

df = st.session_state['vacancies_df']

# Проверяем наличие колонки с навыками
if 'skills' not in df.columns:
    st.error("Колонка 'skills' не найдена. Перезапустите парсинг с обновленным кодом main.py")
    st.stop()

st.title("🛠️ Аналитика технологического стека")
st.markdown(f"Анализ навыков на основе **{len(df)}** вакансий.")

# --- 2. ПОДГОТОВКА ДАННЫХ ДЛЯ ГРАФИКОВ ---
# Превращаем строку навыков обратно в список и считаем их
all_skills_list = []
for s in df['skills'].dropna():
    if s:
        all_skills_list.extend([skill.strip() for skill in s.split(',')])

skill_counts = Counter(all_skills_list)
df_skills = pd.DataFrame(skill_counts.items(), columns=['Skill', 'Count']).sort_values(by='Count', ascending=False)

# --- 3. ВИЗУАЛИЗАЦИЯ 1: ТОП ТЕХНОЛОГИЙ (ОБЩИЙ) ---
st.subheader("🔝 ТОП-20 самых востребованных технологий")

fig_total = px.bar(
    df_skills.head(20),
    x='Count',
    y='Skill',
    orientation='h',
    color='Count',
    color_continuous_scale='Viridis',
    text='Count',
    labels={'Count': 'Количество вакансий', 'Skill': 'Технология'}
)
fig_total.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=False)
st.plotly_chart(fig_total, use_container_width=True)

# --- 4. ВИЗУАЛИЗАЦИЯ 2: СТЕК ПО КАТЕГОРИЯМ ---
st.divider()
st.subheader("🎯 Стек технологий по направлениям")

selected_cat = st.selectbox("Выберите направление для анализа:", options=df['category'].unique())

# Фильтруем навыки только для выбранной категории
cat_skills = []
for s in df[df['category'] == selected_cat]['skills'].dropna():
    if s:
        cat_skills.extend([skill.strip() for skill in s.split(',')])

cat_skill_counts = Counter(cat_skills)
df_cat_skills = pd.DataFrame(cat_skill_counts.items(), columns=['Skill', 'Count']).sort_values(by='Count', ascending=False)

if not df_cat_skills.empty:
    fig_cat = px.pie(
        df_cat_skills.head(10),
        values='Count',
        names='Skill',
        hole=0.4,
        title=f"ТОП-10 инструментов в {selected_cat}",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    st.plotly_chart(fig_cat, use_container_width=True)
else:
    st.info("В этой категории навыки не найдены.")

# --- 5. ТАБЛИЦА СООТВЕТСТВИЯ (ИНСАЙТЫ) ---
st.divider()
st.subheader("💡 Связь: Технология + Зарплата")

# Берем только те вакансии, где указана зарплата (хотя бы 'от')
df_salary = df[df['salary_from'].notnull()].copy()

if not df_salary.empty:
    # Разворачиваем список навыков, чтобы каждая строка была "Один навык - Одна зарплата"
    df_salary['skills_list'] = df_salary['skills'].str.split(',')
    df_exploded = df_salary.explode('skills_list')
    df_exploded['skills_list'] = df_exploded['skills_list'].str.strip()
    
    # Считаем среднюю зарплату по каждому навыку
    skill_salary = df_exploded.groupby('skills_list')['salary_from'].agg(['mean', 'count']).reset_index()
    skill_salary = skill_salary[skill_salary['count'] > 1] # Убираем единичные случаи
    skill_salary.columns = ['Технология', 'Средняя зарплата (от)', 'Кол-во вакансий']
    
    st.write("Средняя предлагаемая зарплата (минимум) для специалистов со знанием:")
    st.dataframe(
        skill_salary.sort_values(by='Средняя зарплата (от)', ascending=False),
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("Недостаточно данных о зарплатах для анализа стека.")
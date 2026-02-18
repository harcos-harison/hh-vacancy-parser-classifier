import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- 1. ПРОВЕРКА ДАННЫХ ---
if 'vacancies_df' not in st.session_state or st.session_state['vacancies_df'] is None:
    st.warning("⚠️ Данные не найдены. Сначала запустите парсер на главной странице.")
    st.stop()

df = st.session_state['vacancies_df'].copy()

# Конвертируем колонку в числа, если они вдруг загрузились как строки
df['salary_from'] = pd.to_numeric(df['salary_from'], errors='coerce')
df['salary_to'] = pd.to_numeric(df['salary_to'], errors='coerce')

# Оставляем только те вакансии, где указана хотя бы минимальная зарплата
df_salary = df.dropna(subset=['salary_from'])

if df_salary.empty:
    st.error("❌ В собранных вакансиях не указаны зарплаты. Нечего анализировать.")
    st.stop()

st.title("💰 Детальный анализ зарплат в IT")
st.markdown(f"Аналитика построена на основе **{len(df_salary)}** вакансий с указанным доходом.")

# --- 2. ОБЩИЕ МЕТРИКИ (KPI) ---
avg_min = df_salary['salary_from'].median()
df_salary['salary_to_clean'] = df_salary['salary_to'].fillna(df_salary['salary_from'] * 1.2)
avg_max = df_salary['salary_to_clean'].median()

m1, m2, m3 = st.columns(3)
# Используем безопасное приведение к int через проверку на NaN
m1.metric("Медианный 'от'", f"{int(avg_min/1000) if pd.notnull(avg_min) else 0}к")
m2.metric("Медианный 'до'", f"{int(avg_max/1000) if pd.notnull(avg_max) else 0}к")
max_val = df_salary['salary_from'].max()
m3.metric("Самый высокий 'от'", f"{int(max_val/1000) if pd.notnull(max_val) else 0}к")

# --- 3. ГРАФИК: ЗАРПЛАТНЫЕ ОБЛАКА ---
st.divider()
st.subheader("📊 Зарплатные вилки по направлениям")

fig_box = px.box(
    df_salary, 
    x="category", 
    y="salary_from", 
    color="category",
    points="all",
    labels={'salary_from': 'Зарплата от (руб.)', 'category': 'Направление'},
    title="Распределение зарплат (точки — конкретные вакансии)"
)
fig_box.update_layout(showlegend=False)
st.plotly_chart(fig_box, use_container_width=True)

# --- 4. ГРАФИК: СРАВНЕНИЕ МИН/МАКС ---
st.divider()
st.subheader("📈 Диапазоны выплат (Медианный Мин. - Макс.)")

salary_stats = df_salary.groupby('category').agg({
    'salary_from': 'median',
    'salary_to_clean': 'median'
}).reset_index()

salary_stats = salary_stats.sort_values('salary_to_clean')

# Очищаем результаты агрегации от NaN перед отрисовкой
salary_stats = salary_stats.dropna(subset=['salary_from', 'salary_to_clean'])

salary_stats['Min'] = (salary_stats['salary_from'] / 1000).round(0)
salary_stats['Max'] = (salary_stats['salary_to_clean'] / 1000).round(0)

fig_sal = go.Figure()
fig_sal.add_trace(go.Bar(
    y=salary_stats['category'],
    x=salary_stats['Max'] - salary_stats['Min'],
    base=salary_stats['Min'],
    orientation='h',
    marker=dict(color='rgba(0, 168, 107, 0.6)', line=dict(color='rgba(0, 168, 107, 1.0)', width=2)),
    name='Медианная вилка'
))

for i, row in salary_stats.iterrows():
    fig_sal.add_annotation(x=row['Min'], y=row['category'], text=f"{int(row['Min'])}к", showarrow=False, xshift=-25)
    fig_sal.add_annotation(x=row['Max'], y=row['category'], text=f"<b>{int(row['Max'])}к</b>", showarrow=False, xshift=30)

fig_sal.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(title="Тысяч рублей"), height=500)
st.plotly_chart(fig_sal, use_container_width=True)

# --- 5. ВЗАИМОСВЯЗЬ: ОПЫТ И ДЕНЬГИ ---
st.divider()
st.subheader("⏳ Сколько стоит опыт?")

exp_salary = df_salary.groupby('experience')['salary_from'].median().reindex(
    ["Нет опыта", "От 1 года до 3 лет", "От 3 до 6 лет", "Более 6 лет"]
).reset_index()

# Ключевое исправление: удаляем строки, где после reindex появились NaN (если таких категорий нет в данных)
exp_salary_clean = exp_salary.dropna(subset=['salary_from'])

if not exp_salary_clean.empty:
    fig_exp_sal = px.line(
        exp_salary_clean, 
        x='experience', 
        y='salary_from', 
        markers=True,
        # Безопасное преобразование в текст
        text=[f"{int(x/1000)}к" for x in exp_salary_clean['salary_from']],
        title="Рост медианной зарплаты 'от' в зависимости от стажа"
    )
    fig_exp_sal.update_traces(textposition="top center", line_color="#FF4B4B", line_width=4)
    fig_exp_sal.update_layout(yaxis_title="Зарплата (руб.)", xaxis_title="Требуемый опыт")
    st.plotly_chart(fig_exp_sal, use_container_width=True)
else:
    st.info("Недостаточно данных для построения графика зависимости зарплаты от опыта.")

# --- 6. ТОП САМЫХ ДОРОГИХ ВАКАНСИЙ ---
st.divider()
st.subheader("💎 ТОП-5 самых высокооплачиваемых вакансий")
top_5 = df_salary.sort_values(by='salary_from', ascending=False).head(5)
st.table(top_5[['name', 'company', 'salary_from', 'category']])
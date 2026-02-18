import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 1. ПРОВЕРКА ДАННЫХ ---
if 'vacancies_df' not in st.session_state or st.session_state['vacancies_df'] is None:
    st.warning("⚠️ Данные не найдены. Сначала запустите парсер на главной странице.")
    st.stop()

# Загружаем реальные данные из сессии
df = st.session_state['vacancies_df']

# --- 2. ПОДГОТОВКА СТАТИСТИКИ ---
# Считаем количество вакансий по категориям
df_stats = df['category'].value_counts().reset_index()
df_stats.columns = ['Category', 'Count']

st.title("📊 Аналитика IT вакансий")
st.markdown(f"**Всего проанализировано:** {len(df)} вакансий")

# --- 3. РАСПРЕДЕЛЕНИЕ ПО НАПРАВЛЕНИЯМ ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Распределение по направлениям")
    fig = px.bar(
        df_stats, 
        x='Category', 
        y='Count',
        text='Count',
        color='Count',
        color_continuous_scale='Viridis',
        labels={'Count': 'Вакансий', 'Category': 'Направление'}
    )
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Таблица лидеров")
    st.dataframe(
        df_stats.sort_values(by='Count', ascending=False),
        hide_index=True,
        use_container_width=True
    )

# --- 4. ИНСАЙТЫ ДЛЯ НОВИЧКА ---
st.divider()
st.subheader("💡 Анализ рынка для входа")

top_cat = df_stats.iloc[0]['Category']
st.info(f"Наибольшее количество предложений сосредоточено в **{top_cat}**. Рекомендуем начинать изучение с этого стека.")

# --- 5. ЗАРПЛАТНЫЕ ВИЛКИ (РЕАЛЬНЫЕ ДАННЫЕ) ---
st.title("💰 Зарплатные вилки в IT (тыс. руб.)")

# Фильтруем только те вакансии, где указана зарплата
df_salary = df.dropna(subset=['salary_from'])

if not df_salary.empty:
    # Группируем по категориям и считаем средний МИН и МАКС
    # Делим на 1000 для формата "к"
    salary_analys = df_salary.groupby('category').agg({
        'salary_from': 'min',
        'salary_to': 'max'
    }).reset_index()
    
    # Если salary_to не указан, берем salary_from + 20% для вилки
    salary_analys['salary_to'] = salary_analys['salary_to'].fillna(salary_analys['salary_from'] * 1.2)
    
    # Переводим в тысячи
    salary_analys['Min'] = (salary_analys['salary_from'] / 1000).round(0)
    salary_analys['Max'] = (salary_analys['salary_to'] / 1000).round(0)
    salary_analys = salary_analys.sort_values('Max')

    fig_sal = go.Figure()
    fig_sal.add_trace(go.Bar(
        y=salary_analys['category'],
        x=salary_analys['Max'] - salary_analys['Min'],
        base=salary_analys['Min'],
        orientation='h',
        marker=dict(color='rgba(55, 128, 191, 0.6)', line=dict(color='rgba(55, 128, 191, 1.0)', width=2)),
        name='Диапазон зарплат',
        hovertemplate='<b>%{y}</b><br>От: %{base}к<br>До: %{x|+.0f}к'
    ))

    # Добавляем аннотации с цифрами
    for i, row in salary_analys.iterrows():
        fig_sal.add_annotation(x=row['Min'], y=row['category'], text=f"{int(row['Min'])}к", showarrow=False, xshift=-30)
        fig_sal.add_annotation(x=row['Max'], y=row['category'], text=f"<b>{int(row['Max'])}к</b>", showarrow=False, xshift=35)

    fig_sal.update_layout(plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(title="Тысяч рублей"), height=500)
    st.plotly_chart(fig_sal, use_container_width=True)
else:
    st.warning("Нет данных о зарплатах для построения графиков.")

# --- 6. АНАЛИЗ СЛОЖНОСТИ ВХОДА (РЕАЛЬНЫЕ ДАННЫЕ) ---
st.title("📈 Анализ сложности входа по направлениям")

# Группируем реальный опыт
df_exp = df.groupby(['category', 'experience']).size().reset_index(name='Количество')
df_exp.columns = ['Направление', 'Опыт', 'Количество']

# Определяем порядок опыта для графика
exp_order = ["Нет опыта", "От 1 года до 3 лет", "От 3 до 6 лет", "Более 6 лет", "Не указан"]

fig_exp = px.bar(
    df_exp, 
    y="Направление", 
    x="Количество", 
    color="Опыт", 
    orientation='h',
    category_orders={"Опыт": exp_order},
    color_discrete_map={
        'Нет опыта': '#C1E1C1', 
        'От 1 года до 3 лет': '#77DD77', 
        'От 3 до 6 лет': '#00A86B',
        'Более 6 лет': '#006400',
        'Не указан': '#D3D3D3'
    },
    barmode="relative"
)

fig_exp.update_layout(xaxis_title="Количество вакансий", yaxis_title="", plot_bgcolor='rgba(0,0,0,0)', height=450)
st.plotly_chart(fig_exp, use_container_width=True)

st.info("💡 Данные обновляются автоматически на основе результатов последнего поиска.")
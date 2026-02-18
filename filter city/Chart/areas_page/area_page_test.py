import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# =========================
# 1. Подготовка данных
# =========================

# Настройка страницы
st.set_page_config(page_title="Dev Market Analytics 2026", layout="wide")

# 1. Подготовка данных (твои реальные цифры)
data = {
    'Category': ['Backend', 'Data', 'Other', 'QA', 'Management', 'Embedded', 'Frontend', 'Support', 'DevOps', 'Fullstack'],
    'Count': [13, 10, 6, 4, 3, 2, 1, 1, 1, 1]
}
df_stats = pd.DataFrame(data)

st.title("📊 Аналитика IT вакансий")
st.markdown(f"**Всего проанализировано:** {df_stats['Count'].sum()} вакансий")

# 2. Создание колонок для интерфейса
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Распределение по направлениям")
    # Используем Plotly для интерактивности
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

# 3. Секция инсайтов для новичка
st.divider()
st.subheader("💡 Анализ рынка для входа")

top_cat = df_stats.iloc[0]['Category']
st.info(f"Наибольшее количество предложений сосредоточено в **{top_cat}**. Рекомендуем начинать изучение с этого стека.")

# Если пользователь ищет Data Science, а у нас только Data
search = st.text_input("Поиск категории (например, Data Science):")
if search:
    if search not in df_stats['Category'].values:
        st.warning(f"Прямого совпадения с '{search}' не найдено. Возможно, вам подойдет категория 'Data'?")
    
    
    
# =========================
# 4. Визуализация зарплатных вилок (пример)
# =========================

# Данные (сократил до тысяч для чистоты)
data = {
    'Category': ['Backend', 'Data', 'QA', 'Management', 'Frontend', 'DevOps'],
    'Min': [120, 130, 80, 200, 100, 150],
    'Max': [450, 500, 220, 600, 380, 550]
}
df = pd.DataFrame(data).sort_values('Max') # Сортируем для красоты

st.title("💰 Зарплатные вилки в IT (тыс. руб.)")

# Создаем пустую фигуру
fig = go.Figure()

# Добавляем "плавающие" бары
fig.add_trace(go.Bar(
    y=df['Category'],
    x=df['Max'] - df['Min'], # Длина бара
    base=df['Min'],          # Точка начала бара
    orientation='h',
    marker=dict(
        color='rgba(55, 128, 191, 0.6)',
        line=dict(color='rgba(55, 128, 191, 1.0)', width=2)
    ),
    name='Диапазон зарплат',
    hovertemplate='<b>%{y}</b><br>От: %{base}к<br>До: %{x|+.0f}к' # Настройка подсказки
))

# Добавляем текстовые метки по краям баров
for i, row in df.iterrows():
    # Метка MIN
    fig.add_annotation(
        x=row['Min'], y=row['Category'],
        text=f"{row['Min']}к", showarrow=False,
        xshift=-30, font=dict(color="gray")
    )
    # Метка MAX
    fig.add_annotation(
        x=row['Max'], y=row['Category'],
        text=f"<b>{row['Max']}к</b>", showarrow=False,
        xshift=35, font=dict(color="#3780BF")
    )

# Настройка стиля фона и осей
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(
        showgrid=True,
        gridcolor='lavender',
        range=[0, df['Max'].max() + 100], # Запас места справа под цифры
        title="Тысяч рублей"
    ),
    yaxis=dict(title=""),
    showlegend=False,
    margin=dict(l=20, r=20, t=20, b=20),
    height=500
)

st.plotly_chart(fig, use_container_width=True)


# =========================
# 5. Анализ сложности входа (пример)
# =========================

# 1. Пример данных (собери их через df.groupby(['category', 'experience']).size())
data = {
    'Направление': ['Backend', 'Backend', 'Backend', 'QA', 'QA', 'QA', 'DevOps', 'DevOps'],
    'Опыт': ['Нет опыта', '1-3 года', '3-6 лет', 'Нет опыта', '1-3 года', '3-6 лет', 'Нет опыта', '1-3 года', '3-6 лет'],
    'Количество': [2, 7, 4, 8, 3, 1, 0, 2, 8] # Твои цифры из парсера
}
df_exp = pd.DataFrame(data)

st.title("📈 Анализ сложности входа по направлениям")
st.write("Какая доля вакансий открыта для новичков, а где ждут только профи?")

# 2. Строим горизонтальный накопленный график
fig = px.bar(
    df_exp, 
    y="Направление", 
    x="Количество", 
    color="Опыт", 
    orientation='h',
    # Приятная палитра: от светлого (новичок) к темному (профи)
    color_discrete_map={
        'Нет опыта': '#C1E1C1', 
        '1-3 года': '#77DD77', 
        '3-6 лет': '#00A86B',
        '6+ лет': '#006400'
    },
    barmode="relative" # Можно использовать "percent", чтобы все полоски были одной длины (100%)
)

# 3. Настройка дизайна
fig.update_layout(
    xaxis_title="Количество вакансий",
    yaxis_title="",
    legend_title="Требуемый опыт",
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(l=20, r=20, t=50, b=20),
    height=400
)

st.plotly_chart(fig, use_container_width=True)
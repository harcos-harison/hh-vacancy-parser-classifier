import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. ПРОВЕРКА session_state ---
if 'vacancies_df' not in st.session_state or st.session_state['vacancies_df'] is None:
    st.warning("⚠️ Данные не найдены. Сначала спарсите вакансии или загрузите корректный файл на главной.")
    st.stop()

df = st.session_state['vacancies_df'].copy()

# --- 2. КОРРЕКЦИЯ КОЛОНОК (Маппинг на лету) ---
# Если вдруг загружен файл с обрезанными заголовками, пытаемся их восстановить
mapping = {
    'experienceatized_co': 'lemmatized_content',
    'alary_fron': 'salary_from',
    'name': 'name'
}
df = df.rename(columns=mapping)

# Проверка критически важных колонок для этой страницы
if 'experience' not in df.columns or 'category' not in df.columns:
    st.error("❌ В файле отсутствуют колонки 'experience' или 'category'. Попробуйте пересобрать данные.")
    st.stop()

# --- 3. ОБРАБОТКА ДАННЫХ ---
df['experience'] = df['experience'].fillna("Не указан")

# Считаем итоги для отображения в легенде/осях
cat_totals = df['category'].value_counts()
df['category_display'] = df['category'].apply(lambda x: f"{x} (всего: {cat_totals.get(x, 0)})")

order = df['category_display'].value_counts().index.tolist()
hh_exp_order = ["Нет опыта", "От 1 года до 3 лет", "От 3 до 6 лет", "Более 6 лет", "Не указан"]

# --- 4. ВИЗУАЛИЗАЦИЯ ---
st.title("📊 Анализ требований к опыту")

exp_stats = df.groupby(['category_display', 'experience']).size().reset_index(name='count')

fig = px.bar(
    exp_stats, 
    y="category_display", 
    x="count", 
    color="experience", 
    orientation='h',
    category_orders={"category_display": order, "experience": hh_exp_order},
    color_discrete_map={
        'Нет опыта': '#B2FFB2', 
        'От 1 года до 3 лет': '#4CAF50',  
        'От 3 до 6 лет': '#2E7D32',    
        'Более 6 лет': '#1B5E20',
        'Не указан': '#D3D3D3'     
    },
    template="plotly_white"
)

fig.update_layout(
    barmode='stack', 
    barnorm='percent', 
    xaxis_title="Доля вакансий (%)",
    yaxis_title=None,
    height=600
)
st.plotly_chart(fig, use_container_width=True)

# --- 5. ВЗВЕШЕННЫЕ ИНСАЙТЫ ---
st.divider()
col1, col2 = st.columns(2)

def get_leader(data, filters):
    res = []
    for cat in data['category'].unique():
        sub = data[data['category'] == cat]
        total = len(sub)
        target = len(sub[sub['experience'].isin(filters)])
        share = target / total if total > 0 else 0
        score = share * np.log1p(total)
        res.append({'cat': cat, 'score': score, 'share': share, 'total': total})
    return pd.DataFrame(res).sort_values('score', ascending=False).iloc[0] if res else None

if not df.empty:
    easy = get_leader(df, ["Нет опыта"])
    hard = get_leader(df, ["От 3 до 6 лет", "Более 6 лет"])

    if easy is not None and easy['share'] > 0:
        with col1:
            st.success(f"✅ **Low Entry Barrier: {easy['cat']}**")
            st.write(f"Доля вакансий без опыта: **{easy['share']*100:.1f}%**")
    
    if hard is not None and hard['share'] > 0:
        with col2:
            st.error(f"🔥 **High Entry Barrier: {hard['cat']}**")
            st.write(f"Доля Senior/Middle+: **{hard['share']*100:.1f}%**")
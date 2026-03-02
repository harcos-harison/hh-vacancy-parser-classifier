import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from typing import Optional

# --- КОНСТАНТЫ ---
HH_EXP_ORDER = ["Нет опыта", "От 1 года до 3 лет", "От 3 до 6 лет", "Более 6 лет", "Не указан"]
COLOR_MAP = {
    'Нет опыта': '#B2FFB2', 
    'От 1 года до 3 лет': '#4CAF50',  
    'От 3 до 6 лет': '#2E7D32',    
    'Более 6 лет': '#1B5E20',
    'Не указан': '#D3D3D3'     
}

# --- 1. ПОДГОТОВКА ДАННЫХ ---

def load_and_prepare_data() -> pd.DataFrame:
    if 'vacancies_df' not in st.session_state or st.session_state['vacancies_df'] is None:
        return pd.DataFrame()

    df = st.session_state['vacancies_df'].copy()
    mapping = {'experienceatized_co': 'lemmatized_content', 'alary_fron': 'salary_from'}
    df = df.rename(columns=mapping)
    
    if not all(col in df.columns for col in ['experience', 'category']):
        return pd.DataFrame()
        
    df['experience'] = df['experience'].fillna("Не указан")
    return df

def get_category_display_names(df: pd.DataFrame) -> pd.DataFrame:
    cat_totals = df['category'].value_counts()
    def format_name(cat):
        count = cat_totals.get(cat, 0)
        prefix = "🔘 " if count < 30 else ""
        return f"{prefix}{cat} ({count} вак.)"
    df['category_display'] = df['category'].apply(format_name)
    return df

# --- 2. ВИЗУАЛИЗАЦИЯ (ГРАФИКИ) ---

def draw_donut_chart(share: float, color: str, center_text: str):
    fig = px.pie(
        values=[share, 1 - share], 
        names=["Доля", "Остальные"],
        hole=0.75, 
        color_discrete_sequence=[color, "#F0F2F6"]
    )
    fig.update_layout(
        showlegend=False, height=160, margin=dict(t=10, b=10, l=10, r=10),
        annotations=[dict(text=center_text, x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    fig.update_traces(textinfo='none', hovertemplate=None)
    return fig

def render_experience_chart(df: pd.DataFrame):
    st.subheader("📊 Распределение опыта по направлениям")
    
    # Считаем количество
    exp_stats = df.groupby(['category_display', 'experience']).size().reset_index(name='count')
    
    # Считаем проценты вручную для каждой категории, чтобы в сумме было 100%
    totals = exp_stats.groupby('category_display')['count'].transform('sum')
    exp_stats['percent'] = (exp_stats['count'] / totals) * 100

    category_order = df['category_display'].value_counts().index.tolist()

    fig = px.bar(
        exp_stats, 
        y="category_display", 
        x="percent", # Используем честный процент
        color="experience", 
        orientation='h',
        category_orders={"category_display": category_order, "experience": HH_EXP_ORDER},
        color_discrete_map=COLOR_MAP, 
        template="plotly_white"
    )

    fig.update_layout(
        barmode='stack', 
        xaxis_title="Доля от 100% вакансий в категории", 
        xaxis_range=[0, 100], 
        yaxis_title=None,
        height=600, 
        legend_title_text="Требуемый опыт"
    )
    
    fig.update_traces(texttemplate='%{x:.1f}%', textposition='inside')
    st.plotly_chart(fig, use_container_width=True)

# --- 3. АНАЛИТИКА (КАРТОЧКИ) ---

def render_insights(df: pd.DataFrame, title: str, is_exact: bool = True):
    st.markdown(f"### {title}")
    col1, col2 = st.columns(2)
    
    # Сбор статистики для поиска лидеров
    summary = []
    for cat in df['category'].unique():
        sub = df[df['category'] == cat]
        t = len(sub)
        no_exp_share = len(sub[sub['experience'] == "Нет опыта"]) / t
        senior_share = len(sub[sub['experience'].isin(["От 3 до 6 лет", "Более 6 лет"])]) / t
        # Score нужен для баланса: доля + объем вакансий (чтобы 1 вакансия не давала 100%)
        score_easy = no_exp_share * np.log1p(t)
        score_hard = senior_share * np.log1p(t)
        summary.append({
            'cat': cat, 'no_exp': no_exp_share, 'senior': senior_share, 
            'total': t, 'score_e': score_easy, 'score_h': score_hard
        })
    
    res_df = pd.DataFrame(summary)
    if res_df.empty: return

    easy = res_df.sort_values('score_e', ascending=False).iloc[0]
    hard = res_df.sort_values('score_h', ascending=False).iloc[0]

    color_g = "#2ECC71" if is_exact else "#A9DFBF"
    color_r = "#E74C3C" if is_exact else "#F1948A"

    with col1:
        with st.container(border=True):
            st.markdown("#### ✅ Самый легкий вход")
            st.markdown(f"**{easy['cat']}**")
            st.plotly_chart(draw_donut_chart(easy['no_exp'], color_g, f"{easy['no_exp']*100:.1f}%"), use_container_width=True)
            st.write(f"Здесь самая большая концентрация вакансий для новичков.")
            st.caption(f"На основе {int(easy['total'])} вакансий")

    with col2:
        with st.container(border=True):
            st.markdown("#### 🔥 Самый высокий барьер")
            st.markdown(f"**{hard['cat']}**")
            st.plotly_chart(draw_donut_chart(hard['senior'], color_r, f"{hard['senior']*100:.1f}%"), use_container_width=True)
            st.write(f"В этом направлении почти не ищут людей без серьезного опыта.")
            st.caption(f"На основе {int(hard['total'])} вакансий")

# --- ГЛАВНЫЙ ЗАПУСК ---

def main():
    df = load_and_prepare_data()
    if df.empty:
        st.warning("⚠️ Данные не найдены. Сначала спарсите вакансии.")
        return

    st.title("🚀 Карьерный навигатор: Опыт работы")
    
    st.info("Ниже показано, какой процент от всех вакансий в каждом направлении занимают требования к опыту. Сумма всех частей в строке всегда равна 100%.")

    # 1. Основной график
    df_display = get_category_display_names(df)
    render_experience_chart(df_display)

    st.divider()

    # 2. Группировка вакансий по количеству
    counts = df['category'].value_counts()
    df_valid = df[df['category'].isin(counts[counts >= 30].index)]
    df_small = df[df['category'].isin(counts[counts < 30].index)]

    # 3. Вывод аналитики
    if not df_valid.empty:
        render_insights(df_valid, "🎯 Точные выводы (от 30 вакансий)", is_exact=True)
    
    if not df_small.empty:
        with st.expander("🔍 Посмотреть направления с малой выборкой"):
            render_insights(df_small, "📉 Предварительные тренды", is_exact=False)

if __name__ == "__main__":
    main()
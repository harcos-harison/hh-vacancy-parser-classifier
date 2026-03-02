import streamlit as st

# Определяем страницу
# url_path="analysis" сделает адрес http://localhost:8501/analysis
analysis_page = st.Page("experience_page/experience.py", title="Опыт аналитика", icon="📊", url_path="experience")
area_page = st.Page("areas_page/area_page.py", title="Направления аналитика", icon="📊", url_path="area")
main_page = st.Page("main_page/main.py", title="Главная страница", icon="📊", url_path="main")
skills_page = st.Page("skills_page/skills.py", title="Навыки аналитика", icon="📊", url_path="skills")
faster_pars = st.Page("main_page/fast_parser.py", title="Быстрый парсинг", icon="📊", url_path="faster_pars")
experiments_page = st.Page("experiments_page/experiments.py", title="Эксперименты", icon="📊", url_path="experiments")
salary_page = st.Page("salary_page/salary.py", title="Зарплата аналитика", icon="📊", url_path="salary")

# Настраиваем навигацию
pg = st.navigation([main_page, analysis_page, area_page, skills_page, salary_page, experiments_page, faster_pars])
# Запускаем навигацию
pg.run()
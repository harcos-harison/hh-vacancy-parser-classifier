import pandas as pd


# =========================
# 4. Анализ распределения по категориям
# =========================
df = pd.read_excel("classified_vacancies.xlsx")


def print_examples_for_category(df, category_name):
    # Фильтруем DataFrame: выбираем только те строки, где категория совпадает с нужной
    filtered_df = df[df["category"] == category_name]
    
    if filtered_df.empty:
        print(f"\nВакансии в категории '{category_name}' не найдены.")
        return

    print(f"\nПримеры вакансий в категории {category_name}:")
    # Берем первые 5 записей
    examples = filtered_df.head(5)
    
    for _, row in examples.iterrows():
        print(f"- {row['name']} (ID: {row['id']})")

# Использование:
print_examples_for_category(df, "Backend")
print_examples_for_category(df, "Data Science")


category_counts = df["category"].value_counts()

print("Распределение вакансий по категориям:")
for category, count in category_counts.items():
    print(f"{category}: {count} вакансий")  



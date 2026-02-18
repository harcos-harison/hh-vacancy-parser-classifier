import pandas as pd

# =========================
# 1. Категории и ключевые слова
# =========================

CATEGORIES = {

    "Fullstack": [
        "fullstack"
    ],

    "Embedded": [
        "embedded", "встраиваем", "микроконтроллер",
        "c++ linux"
    ],

    "Data": [
        "data", "ml", "machine learning", "ai",
        "аналитик данных", "дата-инженер",
        "математик", "data engineer"
    ],

    "DevOps": [
        "devops", "devsecops", "sre", "cloud"
    ],

    "QA": [
        "qa", "тест", "автотест", "тестировщик"
    ],

    "Frontend": [
        "frontend", "react", "vue", "angular"
    ],

    "Backend": [
        "backend", "разработчик", "developer",
        "программист", "python", "java", ".net"
    ],

    "Support": [
        "поддержк", "helpdesk"
    ],

    "Management": [
        "руководитель", "lead", "team lead",
        "владелец продукта", "cto"
    ]
}

# Приоритет проверки (узкие категории раньше)
PRIORITY = [
    "Fullstack",
    "Embedded",
    "Data",
    "DevOps",
    "QA",
    "Frontend",
    "Backend",
    "Support",
    "Management"
]


# =========================
# 2. Функция классификации
# =========================

def classify_title(title):
    title = str(title).lower()

    scores = {cat: 0 for cat in CATEGORIES}

    for category in PRIORITY:
        for keyword in CATEGORIES[category]:
            if keyword in title:
                scores[category] += 1

    best_category = max(scores, key=scores.get)

    if scores[best_category] == 0:
        return "Other"

    return best_category


# =========================
# 3. Чтение Excel
# =========================

df = pd.read_excel("vacancies_Уфа.xlsx")

# Если колонка называется иначе — поменяй здесь
df["category"] = df["name"].apply(classify_title)

# =========================
# 4. Сохранение результата
# =========================

df.to_excel("classified_vacancies.xlsx", index=False)

print("Классификация завершена ✅")

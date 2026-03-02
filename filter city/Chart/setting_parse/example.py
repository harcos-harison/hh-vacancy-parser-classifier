import requests
import json
from datetime import datetime, timedelta
import json
import time
from datetime import datetime

""""
В данном примере мы ищем тег <script> с типом "application/ld+json", который содержит структурированные данные о вакансии.
Если такой тег найден, мы извлекаем его содержимое, превращаем его в словарь Python с помощью json.loads() и затем извлекаем нужные поля, такие как название вакансии, описание, дата публикации и тип занятости.
Если тег не найден, мы просто создаем пустой словарь, и в дальнейшем можно обработать этот случай по своему усмотрению.
"""

# Функция-декоратор для измерения времени выполнения функции
def timer(func):
    def wrapper(*args, **kwargs):
        print("Начало выполнения функции...")
        t_start = time.perf_counter()
        result = func(*args, **kwargs)
        t_end = time.perf_counter()
        print(f"Время выполнения функции: {t_end - t_start:.5f} секунд")
        return result
    return wrapper


# Получаем текущую дату
today = datetime.now()

# Вычитаем, например, 3 месяца
three_months_date = today - timedelta(days=90)
# Вычитаем, например, 2 месяца
two_months_date = today - timedelta(days=60)
# Вычитаем, например, 30 дней
month_date = today - timedelta(days=30)
# Вычитаем, например, 14 дней
week_date = today - timedelta(days=14)
# Вычитаем, например, 7 дней
two_week_date = today - timedelta(days=7)
# Вычитаем, например, 3 дня
three_days_date = today - timedelta(days=3)

# Форматируем в нужный тебе вид: 2026-01-01
formatted_today = today.strftime('%Y-%m-%d')
formatted_month = month_date.strftime('%Y-%m-%d')
formatted_week = week_date.strftime('%Y-%m-%d')
formatted_three_days = three_days_date.strftime('%Y-%m-%d')
formatted_two_months = two_months_date.strftime('%Y-%m-%d')
formatted_two_week_date = two_week_date.strftime('%Y-%m-%d')
formatted_three_months = three_months_date.strftime('%Y-%m-%d')

date_ranges = [
    (formatted_three_months, formatted_two_months),   # 90 → 60
    (formatted_two_months, formatted_month),          # 60 → 30
    (formatted_month, formatted_week),                # 30 → 14
    (formatted_week, formatted_two_week_date),        # 14 → 7
    (formatted_two_week_date, formatted_three_days),  # 7 → 3
    (formatted_three_days, formatted_today),          # 3 → сегодня
]
Experience = ["noExperience", "between1And3", "between3And6", "moreThan6"]

params_vacancy = {
    "text": "python", # Ключевое слово для поиска вакансий
    "per_page": 100, # Максимальное количество вакансий на странице
    "area": 1,  # Город ну или страна
    "page": 0,  # Номер страницы, начнем с 0
    "experience": "noExperience" # Фильтр по опыту, можно менять на другие значения из Experience
}

@timer
def parse_vacancies(params):
    vacancy = {}  # Словарь для хранения вакансий
    seen_ids = set()  # Для отслеживания уже обработанных вакансий

    total_quantity = 0
    n = 0
    number = 0
    
    for data_from, data_to in date_ranges:
        print(f"Собираем вакансии с {data_from} по {data_to}")
        params["date_from"] = data_from
        params["date_to"] = data_to
        
        for exp in Experience:
            
            print(f"Вывод вакансий: {exp}")
            params["experience"] = exp
            params["page"] = 0
            
            while True:
                response = requests.get("https://api.hh.ru/vacancies", params=params)
                data = response.json()
                
                if response.status_code != 200:
                    print(f"Ошибка при запросе: {response.status_code} - {response.text}")
                    break
                
                if not data.get("items"):
                    print("Достигнут конец списка вакансий.")
                    break   
                
                items = data.get("items")
                
                for item in items:
                    if item["id"] in seen_ids:
                        continue

                    seen_ids.add(item["id"])
                    number += 1
                    total_quantity += 1
                    
                    date_str = item["published_at"]
                    date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S%z")
                    
                    vacancy[str(number)] = {
                            "id_hh": item["id"],
                            "name": item["name"],
                            "experience": exp,
                            "date": date_obj.strftime("%Y-%m-%d %H:%M:%S"),
                            "employer": item["employer"]["name"] if item.get("employer") else "N/A",
                            "url": item["alternate_url"]
                    }
                    
                    print(f"#: {number}, {item['id']}, name: {item['name']}")
                params['page'] += 1
                n += 1
    
    with open("vacancy.json", "w", encoding="utf-8") as f:
        json.dump(vacancy, f, ensure_ascii=False, indent=2)     
              
    print(total_quantity)
    # print(f"Вакансии {vacancy}")


if __name__ == "__main__":
    parse_vacancies(params_vacancy)
# print(json.dumps(data, indent=4, ensure_ascii=False))



import requests
import csv

BASE_URL = "https://api.hh.ru/vacancies"
RUSSIA_AREA_ID = 113  # Россия
PER_PAGE = 100         # Максимум для API

def get_vacancies(text, area_id, per_page=PER_PAGE, page=0):
    params = {
        "text": text,
        "area": area_id,
        "per_page": per_page,
        "page": page
    }
    headers = {"User-Agent": "HH-Parser/1.0"}
    response = requests.get(BASE_URL, params=params, headers=headers)
    response.raise_for_status()
    return response.json()

def parse_vacancies(data):
    vacancies = []
    for item in data["items"]:
        salary = item.get("salary")
        address = item.get("address")
        city = address["city"] if address and address.get("city") else item.get("area", {}).get("name", "Не указан")

        vacancies.append({
            "id": item.get("id"),
            "name": item.get("name"),
            "city": city,
            "company": item.get("employer", {}).get("name"),
            "salary_from": salary["from"] if salary else None,
            "salary_to": salary["to"] if salary else None,
            "currency": salary["currency"] if salary else None,
            "url": item.get("alternate_url")
        })
    return vacancies

def get_all_vacancies_russia(text):
    all_vacancies = []
    page = 0

    while True:
        print(f"Загружаем страницу {page + 1}...")
        data = get_vacancies(text=text, area_id=RUSSIA_AREA_ID, per_page=PER_PAGE, page=page)
        vacancies = parse_vacancies(data)
        if not vacancies:
            break

        all_vacancies.extend(vacancies)
        page += 1

        if page >= data.get("pages", 0):
            break

    return all_vacancies

def save_to_csv(vacancies, filename="vacancies_russia.csv"):
    if not vacancies:
        print("Нет вакансий для сохранения.")
        return
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=vacancies[0].keys())
        writer.writeheader()
        writer.writerows(vacancies)
    print(f"Все вакансии сохранены в файл: {filename}")

if __name__ == "__main__":
    keyword = input("Введите ключевое слово вакансии: ").strip()
    vacancies = get_all_vacancies_russia(keyword)

    print(f"\nНайдено всего вакансий по '{keyword}': {len(vacancies)}")
    save_to_csv(vacancies)

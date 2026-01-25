import requests
import csv

BASE_URL = "https://api.hh.ru/vacancies"
AREAS_URL = "https://api.hh.ru/areas"

def get_area_id_by_city(city_name):
    """Находит регион HH API по названию города."""
    response = requests.get(AREAS_URL)
    response.raise_for_status()
    areas = response.json()

    def search_areas(areas_list):
        for area in areas_list:
            if area["name"].lower() == city_name.lower():
                return area["id"]
            if area.get("areas"):
                result = search_areas(area["areas"])
                if result:
                    return result
        return None

    return search_areas(areas)

def get_vacancies_by_region(text, area_id, per_page=20, page=0):
    """Получает вакансии с HH API по региону"""
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
    """Парсит вакансии и возвращает плоский словарь"""
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

def get_all_vacancies(text, city_name, per_page=20, max_pages=100):
    """Собирает все вакансии по региону и фильтрует по городу"""
    area_id = get_area_id_by_city(city_name)
    if not area_id:
        print(f"Регион для города '{city_name}' не найден")
        return []

    print(f"Используем регион ID: {area_id}")
    all_vacancies = []
    page = 0

    while page < max_pages:
        print(f"Загружаем страницу {page + 1}...")
        data = get_vacancies_by_region(text=text, area_id=area_id, per_page=per_page, page=page)
        vacancies = parse_vacancies(data)

        # фильтруем по городу
        vacancies = [v for v in vacancies if v["city"].lower() == city_name.lower()]

        if not vacancies:
            break

        all_vacancies.extend(vacancies)
        page += 1

    return all_vacancies

def save_vacancies_to_csv(vacancies, filename):
    """Сохраняет список вакансий в CSV"""
    if not vacancies:
        print("Нет вакансий для сохранения.")
        return

    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=vacancies[0].keys())
        writer.writeheader()
        writer.writerows(vacancies)

    print(f"Вакансии сохранены в файл: {filename}")


if __name__ == "__main__":
    city = input("Введите город: ").strip()
    text = input("Введите ключевое слово вакансии: ").strip()

    vacancies = get_all_vacancies(text=text, city_name=city, per_page=20)

    total = len(vacancies)
    print(f"\nНайдено {total} вакансий в {city}\n")

    for v in vacancies:
        print("—" * 40)
        print(f"Вакансия: {v['name']}")
        print(f"Компания: {v['company']}")
        print(f"Город: {v['city']}")
        print(f"ЗП: {v['salary_from']} - {v['salary_to']} {v['currency']}")
        print(f"Ссылка: {v['url']}")

    # Сохраняем в CSV
    save_vacancies_to_csv(vacancies, f"vacancies_{city}.csv")

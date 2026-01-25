import requests

BASE_URL = "https://api.hh.ru/vacancies"

def get_vacancies(
    text="python",
    area=113,           # 1 — Москва, 2 — СПб, 113 — Россия
    per_page=20,
    page=0
):
    params = {
        "text": text,
        "area": area,
        "per_page": per_page,
        "page": page
    }

    headers = {
        "User-Agent": "HH-Parser/1.0"
    }

    response = requests.get(BASE_URL, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def parse_vacancies(data):
    vacancies = []

    for item in data["items"]:
        salary = item["salary"]
        vacancies.append({
            "id": item["id"],
            "name": item["name"],
            "area": item["area"]["name"],
            "company": item["employer"]["name"],
            "salary_from": salary["from"] if salary else None,
            "salary_to": salary["to"] if salary else None,
            "currency": salary["currency"] if salary else None,
            "url": item["alternate_url"]
        })

    return vacancies


if __name__ == "__main__":
    data = get_vacancies(
        text="FastAPI",
        area=113
    )

    vacancies = parse_vacancies(data)

    for v in vacancies:
        print("—" * 40)
        print(f"Вакансия: {v['name']}")
        print(f"Компания: {v['company']}")
        print(f"Город: {v['area']}")
        print(f"ЗП: {v['salary_from']} - {v['salary_to']} {v['currency']}")
        print(f"Ссылка: {v['url']}")


import requests
from bs4 import BeautifulSoup as bs
import json

""""
Пример парсинга страницы вакансии по ID с помощью BeautifulSoup и получения данных из JSON-LD
В данном примере мы делаем запрос к странице вакансии, извлекаем JSON-LD данные из тега <script> и парсим их для получения информации о вакансии.
Обратите внимание, что структура страницы может измениться, и в таком случае нужно будет адаптировать код для поиска нужных данных.
Также стоит учитывать, что некоторые данные могут быть доступны только через API, и в этом случае рекомендуется использовать API для получения информации о вакансии.

В данном примере мы ищем тег <script> с типом "application/ld+json", который содержит структурированные данные о вакансии.
Если такой тег найден, мы извлекаем его содержимое, превращаем его в словарь Python с помощью json.loads() и затем извлекаем нужные поля, такие как название вакансии, описание, дата публикации и тип занятости.
Если тег не найден, мы просто создаем пустой словарь, и в дальнейшем можно обработать этот случай по своему усмотрению.
"""

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

BASE_URL = "https://hh.ru/vacancy/"  # URL вакансии по ID
NAMBER_VACANCY = "129932274"  # ID вакансии для примера

def parse_vacancy_by_id(vacancy_id):

    response = requests.get(BASE_URL + vacancy_id, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка при запросе: {response.status_code} - {response.text}")
        return None
    html = response.text

    # Парсим HTML через BeautifulSoup
    soup = bs(html, "html.parser")

    # Ищем тег <script type="application/ld+json">
    script_tag = soup.find("script", type="application/ld+json")
    if script_tag:
        data = json.loads(script_tag.string)  # превращаем в словарь Python
    else:
        data = {}
    return data

def process_vacancy(data):
    if data == None:
        print("Нет данных для обработки.")
        return None
    if data:
        title = data.get("title", "")
        description_html = data.get("description", "")
        date_posted = data.get("datePosted", "")
        employment_type = data.get("employmentType", "")

        desc_soup = bs(description_html, "html.parser")
        description_text = desc_soup.get_text("\n", strip=True)

        # Выводим результат
        print("Название вакансии:", title)
        print("Дата публикации:", date_posted)
        print("Тип занятости:", employment_type)
        print("Описание:\n", description_text)
        return {
            "title": title,
            "date_posted": date_posted,
            "employment_type": employment_type,
            "description": description_text
        }
    else:
        print("Данные о вакансии не найдены.")
    

def main():
    vacancy_data = parse_vacancy_by_id(NAMBER_VACANCY)
    processed_data = process_vacancy(vacancy_data)
    return processed_data

if __name__ == "__main__":
    main()
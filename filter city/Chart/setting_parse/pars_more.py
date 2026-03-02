import json 
from parse_by_id import parse_vacancy_by_id, process_vacancy, BASE_URL, NAMBER_VACANCY
from example import timer

""""
В данном примере мы ищем тег <script> с типом "application/ld+json", который содержит структурированные данные о вакансии.
Если такой тег найден, мы извлекаем его содержимое, превращаем его в словарь Python с помощью json.loads() и затем извлекаем нужные поля, такие как название вакансии, описание, дата публикации и тип занятости.
Если тег не найден, мы просто создаем пустой словарь, и в дальнейшем можно обработать этот случай по своему усмотрению.
"""


with open("vacancy.json", "r", encoding="utf-8") as f:
    data = json.load(f)


@timer
def parse_all_vacancies():
    for key, item in data.items():
        print(key, process_vacancy(parse_vacancy_by_id(item['id_hh'])))
    
if __name__ == "__main__":
    parse_all_vacancies()
import requests
from pprint import pformat

def create_city_id_file_pretty(file_name="city_to_id.py"):
    try:
        res = requests.get("https://api.hh.ru/areas")
        res.raise_for_status()
        areas_list = res.json()

        city_to_id = {}

        def recursive_search(areas):
            for a in areas:
                city_to_id[a["name"].lower()] = a["id"]
                if a.get("areas"):
                    recursive_search(a["areas"])

        recursive_search(areas_list)

        # Красиво форматируем словарь
        pretty_dict = pformat(city_to_id, width=120, sort_dicts=True)

        with open(file_name, "w", encoding="utf-8") as f:
            f.write("# Этот файл сгенерирован автоматически\n")
            f.write("CITY_TO_ID = ")
            f.write(pretty_dict)
            f.write("\n")

        print(f"Файл '{file_name}' успешно создан! Количество городов: {len(city_to_id)}")
        return city_to_id

    except Exception as e:
        print("Ошибка при получении данных HH API:", e)
        return {}

create_city_id_file_pretty()
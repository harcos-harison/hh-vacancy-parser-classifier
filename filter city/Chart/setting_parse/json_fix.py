import yaml
import json


""""
В данном примере мы читаем JSON-файл, который содержит описания вакансий, и очищаем текст описания от специальных символов, таких как Line Separator (U+2028) и Paragraph Separator (U+2029). Эти символы могут вызывать проблемы при обработке текста, поэтому мы заменяем их на обычные переносы строк. После очистки данных мы сохраняем результат в новый YAML-файл, который может быть удобнее для дальнейшей работы.
Обратите внимание, что при сохранении в YAML мы используем параметр allow_unicode=True, чтобы сохранить все символы в их оригинальном виде, а также default_flow_style=False для более читаемого формата.
"""

# 1. Читаем исходник
with open("vacancy_with_numbers.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 2. Чистим "необычные" символы
for item in data:
    if 'description' in item:
        # Убираем Line Separator (U+2028) и Paragraph Separator (U+2029)
        clean_desc = item['description'].replace('\u2028', '\n').replace('\u2029', '\n')
        item['description'] = clean_desc

# 3. Сохраняем чистое
with open("vacancies_ready_numbers.yaml", "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

print("Файл очищен от спецсимволов и сохранен!")
from natasha import (
    Segmenter,
    MorphVocab,
    
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    
    PER,
    NamesExtractor,

    Doc
)

import json
import re

from streamlit import text
from data import *

import sys
import os

from itertools import islice

# Добавляем путь к родительской папке
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from example import timer


# Коды цветов
RED = "\033[91m"
ORANGE = "\033[93m"
BLUE = "\033[94m"
GREEN = "\033[92m"
BOLD = "\033[1m"
RESET = "\033[0m"

""""В данном примере мы читаем JSON-файл, который содержит описания вакансий, и очищаем текст описания от специальных символов, таких как Line Separator (U+2028) и Paragraph Separator (U+2029). Эти символы могут вызывать проблемы при обработке текста, поэтому мы заменяем их на обычные переносы строк. После очистки данных мы сохраняем результат в новый YAML-файл, который может быть удобнее для дальнейшей работы.
Обратите внимание, что при сохранении в YAML мы используем параметр allow_unicode=True, чтобы сохранить все символы в их оригинальном виде, а также default_flow_style=False для более читаемого формата.
"""

segmenter = Segmenter()
morph_vocab = MorphVocab()

emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)

names_extractor = NamesExtractor(morph_vocab)

    
@timer
def lemmatization(text):
    """"
    В данном примере мы выполняем лемматизацию текста описания вакансии с помощью библиотеки Natasha. Мы сначала очищаем текст от специальных символов, оставляя только буквы, цифры и пробелы. Затем мы создаем документ Natasha, разбиваем его на слова, определяем форму слов и получаем их леммы. Результатом является список лемм, который можно использовать для дальнейшего анализа текста.
    Обратите внимание, что лемматизация может не всегда работать идеально, особенно для сложных текстов или специализированной терминологии, поэтому результаты могут потребовать дополнительной обработки или проверки.
    """
    # удалить спецсимволы (оставить буквы, цифры и пробел)
    clean_text = re.sub(r'[^a-zA-Zа-яА-Я0-9\s+#+]', ' ', text)
    # убрать лишние пробелы
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    # 3️⃣ создаём документ
    doc = Doc(clean_text)
    # 4️⃣ разбиваем на слова
    doc.segment(segmenter)
    # 5️⃣ определяем форму слов
    doc.tag_morph(morph_tagger)
    # 6️⃣ получаем леммы
    lemmas = []

    for token in doc.tokens:    
        token.lemmatize(morph_vocab)
        lemmas.append(token.lemma)

    return lemmas 

def found_data_processing(text: list):
    """"
    В данном примере мы ищем в тексте описания вакансии упоминания различных навыков, таких как языки программирования, фреймворки и другие технологии. Мы используем заранее определенный словарь SKILL_MAP, который содержит категории навыков и соответствующие им ключевые слова. Для каждой категории мы проверяем, какие из ключевых слов присутствуют в тексте, и выводим найденные навыки для каждой категории.
    Обратите внимание, что этот пример является базовым и может быть расширен для более сложного анализа текста, например, с использованием регулярных выражений, синонимов или контекстного анализа для более точного определения навыков.
    """
    
    # found_language = [language for language in SKILL_MAP['Languages'] if language in text]
    # found_language = list(set(found_language)) # удаляем дубликаты, если они есть
    # text_remaining = [word for word in text if word not in found_language] # оставляем только те слова, которые не были найдены как языки программирования
    # #print(len(text), len(text_remaining), len(found_language)) # для проверки, сколько слов было в оригинальном тексте, сколько осталось после удаления и сколько языков программирования было найдено
    
    # found_frameworks = [framework for framework in SKILL_MAP['Frameworks'] if framework in text_remaining]
    # found_frameworks = list(set(found_frameworks)) # удаляем дубликаты, если они есть
    # text_remaining = [word for word in text_remaining if word not in found_frameworks] # оставляем только те слова, которые не были найдены как фреймворки
    # #print(len(text), len(text_remaining), len(found_frameworks)) # для проверки, сколько слов было в оригинальном тексте, сколько осталось после удаления и сколько фреймворков было найдено
    
    # аналогично для остальных категорий навыков, например:
    
    found_technologies = {}
    
    print("\n---- разделение по навыкам ----\n")
    SKILL_MAP_LIST = []
    for value in SKILL_MAP:
        SKILL_MAP_LIST.append(value)
    
    for skill in SKILL_MAP_LIST:
        found_skill = [item for item in SKILL_MAP[skill] if item in text]
        
        if found_skill:
            print(f"Найдены {skill}: {found_skill}")
            found_technologies[skill] = found_skill
    
    # Категории для навыков могут быть разными, например: "Languages", "Frameworks", "Tools", "Testing", "Cybersecurity" и т.д. В данном примере мы просто проходим по всем категориям в SKILL_MAP и ищем соответствующие ключевые слова в тексте. Если какие-то навыки из категории найдены, мы выводим их на экран.
    print("\n---- разделение по категориям ----\n")
    CATEGORIES_MAP_LIST = []
    for value in CATEGORIES:
        CATEGORIES_MAP_LIST.append(value)
    
    for category in CATEGORIES_MAP_LIST:
        found_category = [item for item in CATEGORIES[category] if item in text]
        
        if found_category:
            print(f"Найдены {category}: {found_category}")
            found_technologies[category] = found_category
     
    print("\n---- разделение по грейдам ----\n")       
    # Грейды для навыков могут быть разными, например: "Junior", "Middle", "Senior", "Lead" и т.д. В данном примере мы просто проходим по всем грейдам в GRADE_MAP и ищем соответствующие ключевые слова в тексте. Если какие-то грейды из категории найдены, мы выводим их на экран.
    for grade in GRADE_MAP:
        found_grade = [item for item in GRADE_MAP[grade] if item in text]
        if found_grade:
            print(f"Найдены {grade}: {found_grade}")
            found_technologies[grade] = found_grade
    
    profitability_assessment = 0
    
    for count in SKILL_MAP_LIST:
        if count in found_technologies:
            profitability_assessment += len(found_technologies.get(count, []))
            
    pretty_dict = json.dumps(found_technologies, indent=4, ensure_ascii=False)
            
    if profitability_assessment < 6:
        print(f"{RED}Найдено менее 6 навыков: {profitability_assessment} Отклонено: Низкий индекс релевантности ($Score < 6$).\nПричина: Недостаточное количество технических индикаторов для точной классификации стека.  {RESET}")
        return None # если навыков меньше 6, возвращаем None, чтобы не обрабатывать вакансию 
            
    print(f"\n{RED}TEST: {GREEN}{profitability_assessment} - технологий (Оценка релевантности){RED}, {found_technologies} {RESET} \n{ORANGE} \n ---- вывод текста ---- \n {RESET}")
    
    return text


def main():
    """"
    ПО ИТОГУ ЗДЕСЬ МЫ ДЕЛАЕМ ЛЕММАТИЗАЦИЮ И НАХОДИМ НАВЫКИ В ТЕКСТЕ ОПИСАНИЯ ВАКАНСИИ. В РЕЗУЛЬТАТЕ ПОЛУЧАЕМ СПИСОК НАВЫКОВ, КОТОРЫЕ БЫЛИ УПОМЯНУТЫ В ОПИСАНИИ ВАКАНСИИ, РАЗБИТЫХ ПО КАТЕГОРИЯМ (ЯЗЫКИ ПРОГРАММИРОВАНИЯ, ФРЕЙМВОРКИ И Т.Д.).
    """
    # 1. Читаем исходник
    with open("vacancy_description.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for num, item in enumerate(islice(data, 10), 1):  # Обрабатываем только первые 10 элементов для тестирования
        if 'description' in item:
            description_vacancy = item['description']
            
            print(f"\n#################################{GREEN}{BOLD} id: {item['id']}{RESET}  ########################################")
            print(f"{BLUE}{BOLD} №{num} Обрабатываем вакансию{RESET}", found_data_processing(lemmatization(description_vacancy)), " \n")
            
            
main()

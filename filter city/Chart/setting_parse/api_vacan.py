import requests
import json
from bs4 import BeautifulSoup as bs
import aiohttp
import asyncio
import random
import time
# from fake_useragent import UserAgent

""""
Пример парсинга страницы вакансии по ID с помощью API hh.ru
В данном примере мы делаем запрос к API hh.ru для получения информации о вакансии по ее ID. Мы обрабатываем различные статусы ответа, включая успешные запросы, ошибки и случаи, когда нас просят подождать из-за слишком большого количества запросов.
Мы также добавляем случайные задержки между запросами, чтобы избежать блокировки со стороны серв
ера. Результаты сохраняются в JSON-файл для дальнейшего анализа.
Обратите внимание, что для доступа к API hh.ru может потребоваться регистрация и получение токена, а также соблюдение правил использования API.
"""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0",
    "Accept": "application/json",
}
URL = "https://api.hh.ru/vacancies"
sem = asyncio.Semaphore(3)  # максимум 3 запроса одновременно

counter = 0

async def getting_vacancy_by_id(id, session):
    async with sem:
        # 1. Сделаем базовую задержку чуть больше
        await asyncio.sleep(random.uniform(0.4, 2.5))
        t_start = time.perf_counter()
        try:
            async with session.get(f"{URL}/{id}", headers=HEADERS, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    # Извлекаем описание и чистим его
                    desc_html = data.get('description', '')
                    soup = bs(desc_html, "html.parser")
                    text = soup.get_text("\n", strip=True)
                    global counter
                    counter += 1
                    print(f"# {counter}, ✅ ID {id}: Успешно")
                    return {"id": id, "description": text}
                # 2. Добавляем "вежливую" обработку
                if response.status == 429: # Too Many Requests
                    wait_time = int(response.headers.get("Retry-After", 60))
                    print(f"Меня попросили подождать {wait_time} секунд...")
                    await asyncio.sleep(30)  # ждем 30 секунд перед следующим запросом
                    return {"id": id, "error": "429 Too Many Requests"}
                
                elif response.status == 403:
                    print(f"🚨 ID {id}: Ошибка 403 (Доступ запрещен). Нужна пауза.")
                    return {"id": id, "error": "403 Forbidden"}
                
                else:
                    # Важно: .text() это метод, нужен await
                    error_msg = await response.text()
                    print(f"⚠️ ID {id}: Ошибка {response.status}")
                    return {"id": id, "error": response.status}
                    
        except Exception as e:
            print(f"❌ ID {id}: Исключение {str(e)}")
            return {"id": id, "error": str(e)}

async def main():
    with open("vacancy.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Если данные — словарь, берем значения
    source = list(data.values()) if isinstance(data, dict) else data
    
    async with aiohttp.ClientSession() as session:   
        all_results = []
        batch_size = 100
        start_time = time.time() # Общий старт
        batch_start_time = time.time() # Старт текущей сотни

        print(f"🚀 Начинаем сбор {len(source)} вакансий...")

        for i in range(0, len(source), batch_size):
            # Берем срез из 100 элементов
            batch = source[i : i + batch_size]
            
            # Создаем задачи для текущей пачки
            tasks = [getting_vacancy_by_id(item.get('id_hh'), session) for item in batch]
            
            # Ждем выполнения текущей сотни
            batch_results = await asyncio.gather(*tasks)
            all_results.extend(batch_results)
            
            # Считаем время
            current_time = time.time()
            elapsed_batch = current_time - batch_start_time
            total_elapsed = current_time - start_time
            
            print(f"✅ Готово: {len(all_results)}/{len(source)}")
            print(f"⏱ Время на последние {len(batch)} шт: {elapsed_batch:.2f} сек.")
            print(f"⏳ Всего прошло: {total_elapsed / 60:.1f} мин.")
            print("-" * 30)
            
            # Обнуляем время для следующей сотни
            batch_start_time = time.time()
            
            # Вежливая пауза между пачками, чтобы HH не злился
            await asyncio.sleep(random.uniform(5, 10))
    # Сохраняем итог
    with open("vacancy_description.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
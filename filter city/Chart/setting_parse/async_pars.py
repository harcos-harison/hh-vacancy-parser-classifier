import asyncio
import aiohttp
from bs4 import BeautifulSoup as bs
import json
import random

""""
Пример парсинга страницы вакансии по ID с помощью API hh.ru
В данном примере мы делаем запрос к API hh.ru для получения информации о вакансии по ее ID. Мы обрабатываем различные статусы ответа, включая успешные запросы, ошибки и случаи, когда нас просят подождать из-за слишком большого количества запросов.
Мы также добавляем случайные задержки между запросами, чтобы избежать блокировки со стороны серв
ера. Результаты сохраняются в JSON-файл для дальнейшего анализа.
Обратите внимание, что для доступа к API hh.ru может потребоваться регистрация и получение ток"""

counter = 0
timeout = aiohttp.ClientTimeout(total=5)  # общий таймаут для всех запросов

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
sem = asyncio.Semaphore(5)  # максимум 3 запроса одновременно
REQUEST_TIMEOUT = 3  # таймаут для каждого запроса в секундах
BATCH_SIZE = 10  # количество задач в одном пакете

BASE_URL = "https://hh.ru/vacancy/"

async def scraper(vacancy_id, session):
    async with sem:  # ограничение параллелизма
        
        await asyncio.sleep(random.uniform(1, 4))  # небольшая случайная задержка
        try:
            async with session.get(BASE_URL + vacancy_id, headers=headers) as response:
                if response.status != 200:
                    print(f"Ошибка при запросе: {response.status}")
                    return None
                html = await response.text()
                soup = bs(html, "html.parser")
                script_tag = soup.find("script", type="application/ld+json")
                if script_tag:
                    global counter
                    counter += 1
                    print(f"{counter} Успешно извлечены данные для вакансии ID: {vacancy_id}")
                    return json.loads(script_tag.string)
                else: 
                    print(f"Ошибка: в получении данных из application/ld+json для вакансии ID: {vacancy_id} \nscript_tag: {script_tag} \nresponse.status: {response.status} \n{soup}")  # выводим первые 500 символов для диагностики
                    await asyncio.sleep(10)  # пауза перед следующим запросом при ошибке
                    return {} 
        except asyncio.TimeoutError:
            print(f"⏳ Таймаут для вакансии {vacancy_id}")
            return None
        except aiohttp.ClientError as e:
            print(f"⚠️ Ошибка запроса {vacancy_id}: {e}")
            return None
        
async def main():
    with open("vacancy.json", "r", encoding="utf-8") as f:
        data = list(json.load(f).values())

    results = []

    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
        for i in range(0, len(data), BATCH_SIZE):
            batch = data[i:i+BATCH_SIZE]
            tasks = [asyncio.create_task(scraper(item["id_hh"], session)) for item in batch]
            
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
            
            print(f"✅ Пакет {i//BATCH_SIZE + 1} из {((len(data)-1)//BATCH_SIZE)+1} завершён")
            
            await asyncio.sleep(1)  # пауза между пакетами, чтобы сервер не заблокировал

    with open("vacancy_description.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(main())
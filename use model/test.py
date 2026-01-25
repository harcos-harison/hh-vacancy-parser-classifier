import csv
from transformers import pipeline

# GPU + float16
classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    device=0,
    torch_dtype="auto"
)

CATEGORIES = ["backend", "frontend", "mobile", "data-science", "devops", "qa", "project management"]

input_file = "vacancies_набережные челны.csv"
output_file = "vacancies_набережные челны_classified.csv"
batch_size = 8  # количество вакансий за раз

# Читаем CSV
with open(input_file, encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Классификация батчами
for i in range(0, len(rows), batch_size):
    batch = rows[i:i+batch_size]
    texts = [f"{r['name']} {r.get('description','')}" for r in batch]
    results = classifier(texts, candidate_labels=CATEGORIES)
    
    # если batch_size=1, возвращается dict, иначе list
    if isinstance(results, dict):
        results = [results]
        
    for r, res in zip(batch, results):
        r["category"] = res["labels"][0]
        r["score"] = res["scores"][0]

# Сохраняем CSV
with open(output_file, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Классификация завершена. Результат сохранён в {output_file}")

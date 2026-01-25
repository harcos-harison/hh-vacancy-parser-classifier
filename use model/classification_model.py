from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-mnli")
model = AutoModelForSequenceClassification.from_pretrained("facebook/bart-large-mnli")

text = "Python-разработчик на Django и PostgreSQL"
inputs = tokenizer(text, return_tensors="pt")
outputs = model(**inputs)

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification

# Словарь эмоций (без токсичности)
EMOTIONS = {
    'admiration': 'восхищение', 'amusement': 'веселье', 'anger': 'злость',
    'annoyance': 'раздражение', 'approval': 'одобрение', 'caring': 'забота',
    'confusion': 'непонимание', 'curiosity': 'любопытство', 'desire': 'желание',
    'disappointment': 'разочарование', 'disapproval': 'неодобрение', 'disgust': 'отвращение',
    'embarrassment': 'смущение', 'excitement': 'возбуждение', 'fear': 'страх',
    'gratitude': 'признательность', 'grief': 'горе', 'joy': 'радость',
    'love': 'любовь', 'nervousness': 'нервозность', 'optimism': 'оптимизм',
    'pride': 'гордость', 'realization': 'осознание', 'relief': 'облегчение',
    'remorse': 'раскаяние', 'sadness': 'грусть', 'surprise': 'удивление',
    'neutral': 'нейтральность'
}


# Загружаем обновленную модель и токенизатор
model_path = "./rubert_finetuned"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)

# Классификатор
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer, top_k=32, device=-1)

# Разделение эмоций и токсичности
def process_predictions(predictions):
    emotion_scores = {}

    for res in predictions:
        label = res["label"].replace("__label__", "")  # Убираем "__label__"
        score = res["score"]

        if label in EMOTIONS:
            emotion_scores[EMOTIONS[label]] = emotion_scores.get(EMOTIONS[label], 0) + score

    return emotion_scores

# Входной текст
text = "Ты ужасный человек, мне отвратительно с тобой общаться."

# Анализ текста
predictions = classifier(text, truncation=True, max_length=512)
emotion_scores = process_predictions(predictions[0])

# Вывод результатов
print("\n🎭 Эмоции:")
for label, score in sorted(emotion_scores.items(), key=lambda x: -x[1]):
    print(f"{label}: {round(score * 100, 2)}%")


from fastapi import APIRouter
from transformers import pipeline

router = APIRouter()

model_path = r"E:\Codes\Diplom\Server\rubert_finetuned"

classifier = pipeline("zero-shot-classification",
                      model=model_path,
                      tokenizer=model_path)

ENGLISH_TO_RUSSIAN = {
    'admiration': 'восхищение',
    'amusement': 'веселье',
    'anger': 'злость',
    'annoyance': 'раздражение',
    'approval': 'одобрение',
    'caring': 'забота',
    'confusion': 'непонимание',
    'curiosity': 'любопытство',
    'desire': 'желание',
    'disappointment': 'разочарование',
    'disapproval': 'неодобрение',
    'disgust': 'отвращение',
    'embarrassment': 'смущение',
    'excitement': 'возбуждение',
    'fear': 'страх',
    'gratitude': 'признательность',
    'grief': 'горе',
    'joy': 'радость',
    'love': 'любовь',
    'nervousness': 'нервозность',
    'optimism': 'оптимизм',
    'pride': 'гордость',
    'realization': 'осознание',
    'relief': 'облегчение',
    'remorse': 'раскаяние',
    'sadness': 'грусть',
    'surprise': 'удивление',
    'neutral': 'нейтральность'
}

CANDIDATE_LABELS = list(ENGLISH_TO_RUSSIAN.keys())

@router.post("/analyze")
async def analyze_text(text):
    res = classifier(
        text,
        candidate_labels=CANDIDATE_LABELS,
        hypothesis_template="{}"
    )

    output = []
    for label, score in zip(res["labels"], res["scores"]):
        ru_label = ENGLISH_TO_RUSSIAN.get(label, label)
        output.append({
            "label": ru_label,
            "score": round(score, 4)
        })

    return output[:3]



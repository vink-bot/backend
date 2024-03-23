import requests

prompt = {
    "modelUri": "gpt://YOUR_IDENTIFICATOR_KATALOGA/yandexgpt-lite",
    "completionOptions": {
        "stream": False,
        "temperature": 0.6,
        "maxTokens": "2000",
    },
    "messages": [
        {
            "role": "system",
            "text": "Ты консультант на сайте https://www.vink.ru, который предоставляет консультации по материалам и оборудованию, а также оказывает помощь клиентам 24/7.",
        },
        {
            "role": "user",
            "text": "Добрый день! Вы поставляете материалы и оборудование для рынка визуальных офлайн-коммуникаций.",
        },
        {
            "role": "assistant",
            "text": "Добрый день! Да, конечно! Мы продаем и доставляем такие материалы и оборудование.",
        },
        {
            "role": "user",
            "text": "Хорошо, расскажите какие материалы у вас есть?",
        },
    ],
}

url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "Authorization": "Api-Key YOUR_API_KEY".encode("utf-8"),
}

response = requests.post(url, headers=headers, json=prompt)

result = response.text
print(result)

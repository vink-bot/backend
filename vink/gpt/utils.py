import requests


def send_message_gpt(message):
    prompt = {
        "modelUri": "gpt://b1gpm5j7r2h5egbhgo2e/yandexgpt-lite",
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
                "text": "Добрый день! Торгуете материалами и оборудованием для рынка визуальных офлайн-коммуникаций?",
            },
            {
                "role": "assistant",
                "text": "Добрый день! Да торгуем. Мы продаем и доставляем такие материалы и оборудование.",
            },
            {
                "role": "user",
                "text": message,
            },
        ],
    }
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": "Api-Key AQVNy3UCV8LfNsRlUawiq_Ac9Ior7IBcMkcFQWt8".encode(
            "utf-8"
        ),
    }
    response = requests.post(url, headers=headers, json=prompt)
    responce_data = response.json()
    return responce_data["result"]["alternatives"][0]["message"]["text"]

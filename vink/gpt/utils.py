import requests


def send_message_gpt(message):
    prompt = {
        "modelUri": "gpt://YOUR_IDENTIFICATOR_KATALOGA/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "2000",
        },
        "messages": [
            {
                "role": "user",
                "text": message,
            }
        ],
    }
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Authorization": "Api-Key YOUR_API_KEY".encode("utf-8"),
    }
    response = requests.post(url, headers=headers, json=prompt)
    return response.text

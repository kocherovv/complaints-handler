import requests
import asyncio
import os
import logging
from openai import AsyncOpenAI

openai_client = AsyncOpenAI()
log = logging.getLogger("default")

sentiment_api_key = os.environ.get('SENTIMENT_API_KEY')


async def get_sentiment_async(complaint_text: str):
    url = "https://api.apilayer.com/sentiment/analysis"
    headers = {
        "apikey": sentiment_api_key
    }
    payload = complaint_text.encode("utf-8")

    def do_request():
        r = requests.post(url, headers=headers, data=payload)
        return r

    response = await asyncio.to_thread(do_request)

    if response.status_code != 200:
        log.error("get_sentiment: %s, %s", response.status_code, response.text)
        return "unknown"

    result = response.json().get("sentiment", "").lower()
    log.debug("get_sentiment: %s", result)
    mapping = {
        "positive": "positive",
        "negative": "negative",
        "neutral": "neutral"
    }
    return mapping.get(result, "unknown")


async def get_category_async(complaint_text: str):
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f'Определи категорию жалобы: "{complaint_text}". '
                               f'Варианты: техническая, оплата, другое. Ответ только одним словом.'
                }
            ]
        )

        log.debug("get_category: %s", response.json)
        category = response.choices[0].message.content.strip().lower()
        log.debug("get_category: %s", category)
        valid_categories = {"техническая", "оплата", "другое"}
        return category if category in valid_categories else "другое"

    except Exception as e:
        log.error("get_category error: %s", str(e))
        return "другое"
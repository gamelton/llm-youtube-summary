#!/usr/bin/env python3

import os
import json
import requests
import re
import yt_dlp

OLLAMA_URL = "http://192.168.3.14:11434/api/chat"
YOUTUBE_URL = 'https://www.youtube.com/watch?v=umbtgR77mR8'

for lang in ['ru', 'en']:
    try:
        YDL = yt_dlp.YoutubeDL({'skip_download': True, 'quiet': True, 'writesubtitles': True, 'writeautomaticsub': True, 'subtitlesformat': 'json3', 'subtitleslangs': [lang], 'outtmpl': {'default': 'temp_subtitles_%(id)s'}})
        VIDEO_INFO = YDL.extract_info(YOUTUBE_URL, download=True)
        VIDEO_NAME = VIDEO_INFO.get('title', 'Unknown')
        VIDEO_ID = VIDEO_INFO.get('id', 'unknown')
        break
    except yt_dlp.utils.DownloadError:
        continue

with open(f"temp_subtitles_{VIDEO_ID}.{lang}.json3", "r", encoding="utf-8") as f:
    JSON_SUBTITLES = json.load(f)

SUBTITLE_TEXT = ""
for event in JSON_SUBTITLES.get("events", []):
    if "segs" in event:
        for seg in event["segs"]:
            text = seg.get("utf8", "")
            if text != "\n":
                SUBTITLE_TEXT += text

os.remove(f"temp_subtitles_{VIDEO_ID}.{lang}.json3")

LLM_REQUEST = f"""
Ты — инструмент извлечения фактической информации. 
Тебе даны субтитры из видео: "{VIDEO_NAME}".

Твоя ЗАДАЧА:
Извлечь строго и только ТО, что ПРЯМО и ЯВНО содержится в предоставленном тексте:

— факты
— утверждения
— конкретные тезисы
— имена, фамилии, названия
— даты, временные указания
— числовые данные
— явно упомянутые объекты и события

Ответ строго на русском языке.

Текст субтитров:

{SUBTITLE_TEXT}
"""


JSON_REQUEST = {"model": "gemma3:4b", "stream": False, "messages": [{ "role": "user", "content": f"{LLM_REQUEST}" }], "options": { "num_ctx": 8192 }}
response = requests.post(OLLAMA_URL, json=JSON_REQUEST, headers={"Content-Type": "application/json"})
LLM_RESPONSE_CONTENT = response.json()["message"]["content"]

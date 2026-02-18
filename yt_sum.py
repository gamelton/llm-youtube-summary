#!/usr/bin/env python3

## System packages: ffmpeg, ollama (separate server)
## Python packages: yt-dlp[default,curl-cffi]
## EJS: 
### curl -fsSL https://deno.land/install.sh | sh
### source ~/.bashrc
### pip install -U "yt-dlp[default]" --break-system-packages
# yt-dlp --skip-download --write-auto-sub --sub-lang ru --sub-format json3 -v "YOUR_VIDEO_URL"


import yt_dlp
import glob
import json
import time
import re
import os
import requests
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# --- Configuration ---
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "your-model-name"
YOUTUBE_URL = "https://www.youtube.com/watch?v=REPLACE_ME"

# --- Main logic ---
url = YOUTUBE_URL

if "youtube.com" not in url and "youtu.be" not in url:
    raise ValueError("Please provide a valid YouTube URL.")

video_id = None
lang = None
summary = None

try:
    sub_json = None

    for lang in ['ru', 'en']:
        try:
            with yt_dlp.YoutubeDL({
                'skip_download': True, 'quiet': True, 'writesubtitles': True,
                'writeautomaticsub': True, 'subtitlesformat': 'json3', 'subtitleslangs': [lang],
                'outtmpl': {'default': 'temp_subs_%(id)s', 'subtitle': 'temp_subs_%(id)s'}
            }) as ydl:
                info = ydl.extract_info(url, download=True)
                video_id = info.get('id', 'unknown')
                title = info.get('title', 'Unknown')

                matches = glob.glob(f"*{video_id}*.{lang}.json3")
                logger.info("Looking for %s subtitles, found files: %s", lang, matches)

                if matches:
                    with open(matches[0], "r", encoding="utf-8") as f:
                        sub_json = json.load(f)
                    break
        except yt_dlp.utils.DownloadError:
            time.sleep(5)
            continue

    if not sub_json:
        raise RuntimeError("No subtitles found in ru/en.")

    print("Processing subtitles…")
    lines, prev_end = [], 0

    for ev in sub_json.get("events", []):
        if "segs" not in ev:
            continue
        line = "".join(s.get("utf8", "") for s in ev["segs"]).strip()
        if not line or line == "\n":
            continue
        if lines and line in " ".join(lines[-3:]):
            continue
        start = ev.get("tStartMs", 0)
        dur = ev.get("dDurationMs", 0)
        if lines and start - prev_end > 180_000:
            lines.append("\n\n")
        lines.append(line)
        prev_end = start + dur

    subtitle_text = " ".join(lines).replace("  ", " ").strip()

    if not subtitle_text:
        raise RuntimeError("Subtitles are empty after cleaning.")

    token_est = len(subtitle_text) // 3
    print(f"Sending to LLM (~{token_est} tokens)…")

    system = (
        "Ты — ассистент для создания структурированных конспектов видео из субтитров. "
        "Исправляй ошибки распознавания речи. Отвечай строго на русском. "
        "Не выдумывай то, чего нет в тексте. Пропускай рекламные вставки."
    )
    user_prompt = (
        f'Видео: «{title}»\n\nСоставь структурированный конспект:\n'
        f'## Краткое содержание\n(2-3 предложения)\n'
        f'## Основные тезисы\n(нумерованный список)\n'
        f'## Ключевые факты и данные\n(имена, даты, числа — только явно упомянутые)\n'
        f'## Выводы автора\n(если есть)\n\nТекст субтитров:\n\n{subtitle_text}'
    )

    resp = requests.post(
        OLLAMA_URL,
        headers={"Content-Type": "application/json"},
        json={
            "model": OLLAMA_MODEL,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user_prompt},
            ],
            "options": {
                "num_ctx": max(32768, token_est + 4096),
                "temperature": 0.3,
            },
        },
    )
    resp.raise_for_status()

    summary = re.sub(
        r"<think>.*?</think>\s*", "",
        resp.json()["message"]["content"],
        flags=re.DOTALL,
    ).strip()

    print(f"✅ Summary for: {title}\n")
    print(summary)

except requests.exceptions.Timeout:
    print("❌ LLM request timed out.")
except Exception as e:
    logger.error("Error: %s", e, exc_info=True)
    print(f"❌ Error: {e}")
finally:
    if video_id:
        for f in glob.glob(f"*{video_id}*.json3"):
            try:
                os.remove(f)
            except OSError:
                pass

# YouTube Video Summarizer

A standalone Python script that downloads subtitles from a YouTube video,
processes them, and sends the text to a local [Ollama](https://ollama.com/) LLM
to produce a structured summary in Russian.

---

## Prerequisites

| Requirement | Details |
|---|---|
| **Python** | 3.9 or newer |
| **Ollama** | Running locally (or on a reachable host) with at least one model pulled |
| **ffmpeg** | Required by yt-dlp for some extraction scenarios. Install via your package manager (see below) |

### Installing ffmpeg

```bash
# Ubuntu / Debian
sudo apt update && sudo apt install ffmpeg

# macOS (Homebrew)
brew install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg
```



### Pulling an Ollama model

Make sure the Ollama server is running, then pull the model you plan to use:

```bash
ollama pull gemma3:27b        # or any model you prefer
```

---

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/gamelton/llm-youtube-summary.git
   cd llm-youtube-summary
   ```

2. **Create a virtual environment (recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux / macOS
   venv\Scripts\activate      # Windows
   ```

3. **Install Python dependencies**

   ```bash
   curl -fsSL https://deno.land/install.sh | sh
   source ~/.bashrc
   pip install -U "yt-dlp[default,curl-cffi]" --break-system-packages
   ```

---

## Configuration

Open `yt_sum.py` and edit the variables at the top:

```python
OLLAMA_URL   = "http://localhost:11434/api/chat"   # Ollama API endpoint
OLLAMA_MODEL = "gemma3:27b"                        # Model name you pulled
YOUTUBE_URL  = "https://www.youtube.com/watch?v=REPLACE_ME"
```

| Variable | Description |
|---|---|
| `OLLAMA_URL` | Full URL to the Ollama `/api/chat` endpoint. Change the host/port if Ollama runs on another machine. |
| `OLLAMA_MODEL` | The exact model tag as shown by `ollama list`. |
| `YOUTUBE_URL` | The YouTube video you want to summarize. |

---

## Usage

```bash
python yt_sum.py
```

### What happens

1. **Subtitle download** — the script uses `yt-dlp` to fetch subtitles
   (first Russian, then English) in `json3` format.
2. **Text cleaning** — duplicate lines, empty segments, and large gaps are
   handled; the raw subtitle JSON is collapsed into plain text.
3. **LLM summarization** — the cleaned text is sent to Ollama with a system
   prompt that asks for a structured outline (brief summary, key points,
   facts & data, author's conclusions).
4. **Output** — the summary is printed to the console **and** stored in the
   `summary` Python variable for further programmatic use.

### Example output

```
Processing subtitles…
Sending to LLM (~12045 tokens)…
✅ Summary for: Example Video Title

## Краткое содержание
...

## Основные тезисы
1. ...
2. ...

## Ключевые факты и данные
- ...

## Выводы автора
- ...
```



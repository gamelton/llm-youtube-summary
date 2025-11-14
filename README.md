# YouTube Video Summarizer

A Python tool that automatically generates summaries of YouTube videos by extracting and analyzing their subtitles using a local neural network via Ollama.

## Features

- Extracts subtitles from YouTube videos using `yt-dlp`
- Uses local LLM (via Ollama) to generate summaries
- Extracts key information: facts, names, dates, numerical data

## Prerequisites

Before using this tool, make sure you have:

- **Python 3.7+** installed
- **Ollama** running locally with the `gemma3:4b` model (or modify for your preferred model)
- Required Python packages (see Installation)

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd llm-youtube-summary
```

2. Install required Python packages:
```bash
pip install yt-dlp requests
```

3. Set up Ollama:
```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai/

# Pull the required model
ollama pull gemma3:4b
```

4. Ensure Ollama is running on `http://192.168.3.14:11434` or modify the `OLLAMA_URL` in the script.

## Usage

1. Edit the `YOUTUBE_URL` variable in the script to point to your desired YouTube video:
```python
YOUTUBE_URL = 'https://www.youtube.com/watch?v=your_video_id_here'
```

2. Run the script:
```bash
python yt_sum.py
```

## How It Works

1. **Subtitle Extraction**: The script uses `yt-dlp` to download subtitles in JSON3 format, trying Russian first, then English
2. **Text Processing**: Extracts and cleans the subtitle text from the JSON structure
3. **LLM Analysis**: Sends the cleaned text to Ollama with specific instructions to extract factual information
4. **Summary Generation**: The LLM returns a concise summary containing only explicitly mentioned facts and data

## Configuration

You can customize the following variables in the script:

- `OLLAMA_URL`: Change to your Ollama server address
- `YOUTUBE_URL`: The YouTube video to summarize
- Model: Change `"gemma3:4b"` to use a different Ollama model



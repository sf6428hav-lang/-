# Short Drama Script Generator

A tool for generating formatted drama scripts from short video links (Douyin, Hongguo).

## Quick Start

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env to add your Gemini API key
python -m uvicorn app.main:app --reload --port 8000
```

Then open http://localhost:8000

## Features

- Paste Douyin or Hongguo video links
- Automatic video download and Gemini 3.1 Pro analysis
- Outputs formatted scripts in the "Mahjong" drama format
- Download as .docx or .txt
- Generation history with sidebar view
- Batch generation with progress tracking

## Tech Stack

- Backend: Python FastAPI
- Frontend: Pure HTML + CSS + JavaScript
- Database: SQLite
- AI: Gemini 2.5 Pro multimodal API

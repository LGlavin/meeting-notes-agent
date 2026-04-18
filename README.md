# Meeting Notes Agent

Upload a meeting recording or paste a transcript. The LangGraph agent transcribes it with Whisper, extracts action items and decisions, tracks follow-ups across meetings, and saves structured notes to Airtable.

**Live demo:** https://lzx2ss7cstd9aeqffrbjae.streamlit.app/

## Tech Stack

LangGraph / LangSmith / OpenAI Whisper / Airtable / Streamlit

## How it works

1. Audio is transcribed using OpenAI Whisper
2. The LangGraph agent checks Airtable for past meetings with the same attendees
3. It generates structured notes: summary, action items, decisions, follow-ups
4. It flags which previous follow-ups were addressed and which are still open
5. Notes are saved to Airtable for tracking

## Run locally

1. Clone the repo
2. Copy `.env.example` to `.env` and add your keys
3. `pip install -r requirements.txt`
4. `streamlit run app.py`

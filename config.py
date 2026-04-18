import os
from dotenv import load_dotenv

load_dotenv()

LLM_MODEL = "gpt-4o-mini"
WHISPER_MODEL = "whisper-1"
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY", "")
AIRTABLE_BASE_ID = os.getenv("AIRTABLE_BASE_ID", "")
AIRTABLE_TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "Table 1")
MAX_ITERATIONS = 10

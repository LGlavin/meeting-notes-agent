from openai import OpenAI
from config import WHISPER_MODEL


def transcribe_audio(file_path: str) -> str:
    """Transcribe an audio/video file using OpenAI Whisper."""
    client = OpenAI()
    with open(file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=audio_file,
            response_format="text",
        )
    return transcript

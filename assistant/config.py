# ---------------------------
# assistant/config.py
# Loads env variables and centralises constants used by other modules.
# ---------------------------

from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env from project root (fallback to environment)
load_dotenv()

ACCESS_KEY: str | None = os.getenv("ACCESS_KEY")
WAKE_KEYWORD: str = os.getenv("WAKE_KEYWORD", "jarvis").lower()
VOICE_ID: str | None = os.getenv("VOICE_ID")  # DO NOIT USE
TTS_RATE: int = int(os.getenv("TTS_RATE", "180"))  # words per minute
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

# 🔊 Aufnahme-Parameter
LISTEN_TIMEOUT: int = int(os.getenv("LISTEN_TIMEOUT", "5"))
PHRASE_LIMIT: int = int(os.getenv("PHRASE_LIMIT", "8")) 

if not ACCESS_KEY:
    raise RuntimeError(
        "Porcupine ACCESS_KEY missing. Add it to your .env file or environment."
    )

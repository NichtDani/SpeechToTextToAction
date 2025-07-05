# ---------------------------
# assistant/tts.py
# Thread‑safe text‑to‑speech helper built around pyttsx3.
# ---------------------------

import pyttsx3
from threading import Lock
from .config import TTS_RATE, VOICE_ID
import logging

log = logging.getLogger(__name__)

_engine = pyttsx3.init()
_engine.setProperty("rate", TTS_RATE)
if VOICE_ID:
    _engine.setProperty("voice", VOICE_ID)

_lock = Lock()

# Speak given text synchronously; guarded by a lock.
def speak(text: str) -> None:
    with _lock:
        log.debug("Speaking: %s", text)
        _engine.say(text)
        _engine.runAndWait()
# ---------------------------
# assistant/commands.py
# Parse and execute high‑level voice commands.
# ---------------------------

import sys
import webbrowser
import logging
from .tts import speak

log = logging.getLogger(__name__)


def interpret(text: str) -> str:
    text = text.lower()
    if "öffne youtube" in text:
        return "OPEN_YOUTUBE"
    if "stopp" in text or "stop" in text:
        return "STOP"
    return "UNKNOWN"


def execute(action: str) -> None:
    if action == "OPEN_YOUTUBE":
        speak("Youtube wird geöffnet.")
        webbrowser.open("https://youtube.com")
    elif action == "STOP":
        speak("Der Assistent wird beendet.")
        sys.exit(0)
    else:
        speak("Befehl nicht erkannt.")
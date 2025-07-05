# ---------------------------
# assistant/__main__.py
# assistant entry‑point
# ---------------------------

import logging
from .config import LOG_LEVEL
from .audio import select_microphone, WakeListener, SpeechRecognizer
from .commands import interpret, execute
from .tts import speak
from .config import WAKE_KEYWORD

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s — %(levelname)s — %(message)s",
)
log = logging.getLogger(__name__)


def main() -> None:
    mic_index = select_microphone()
    recognizer = SpeechRecognizer(mic_index)
    speak("Assistent bereit.")  # greet user
    with WakeListener(mic_index) as wake:
        log.info("Warte auf Wakeword '%s'...", WAKE_KEYWORD)
        while True:
            if wake.triggered():
                log.info("Wakeword erkannt.")
                speak("Ja?")
                text = recognizer.listen()
                if text:
                    log.info("Erkannt: %s", text)
                    action = interpret(text)
                    execute(action)
                else:
                    speak("Ich konnte dich nicht verstehen.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        speak("Auf Wiedersehen!")
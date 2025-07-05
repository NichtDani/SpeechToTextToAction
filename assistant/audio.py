# ---------------------------
# assistant/audio.py
# Audio input, wake‑word detection (Porcupine) and speech recognition.
# Refactored: reuse Microphone instance, robust resource handling.
# ---------------------------

from __future__ import annotations
import logging
import struct
from contextlib import AbstractContextManager

import pvporcupine
import pyaudio
import speech_recognition as sr

from .config import (
    ACCESS_KEY,
    WAKE_KEYWORD,
    LISTEN_TIMEOUT,
    PHRASE_LIMIT,
)

log = logging.getLogger(__name__)


def list_microphones() -> list[tuple[int, str]]:
    pa = pyaudio.PyAudio()
    devices = [
        (i, pa.get_device_info_by_index(i)["name"])
        for i in range(pa.get_device_count())
        if pa.get_device_info_by_index(i)["maxInputChannels"] > 0
    ]
    pa.terminate()
    return devices


def select_microphone(index: int | None = None) -> int:
    devices = list_microphones()
    if index is not None:
        return index
    for i, name in devices:
        print(f"{i}: {name}")
    while True:
        try:
            return int(input("🎙️  Bitte Mikro-Index eingeben: "))
        except ValueError:
            print("❌  Ungültige Zahl.")


class WakeListener(AbstractContextManager):
    """
    Context‑manager wrapper around Porcupine & PyAudio.
    Keeps the stream open for the entire lifetime of the listener.
    """

    def __init__(self, mic_index: int, sensitivity: float = 0.5):
        self.porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keywords=[WAKE_KEYWORD],
            sensitivities=[sensitivity],
        )
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            input_device_index=mic_index,
            frames_per_buffer=self.porcupine.frame_length,
        )

    def __enter__(self) -> "WakeListener":
        return self

    def triggered(self) -> bool:
        pcm = self.stream.read(
            self.porcupine.frame_length, exception_on_overflow=False
        )
        pcm_unpacked = struct.unpack_from(
            "h" * self.porcupine.frame_length, pcm
        )
        return self.porcupine.process(pcm_unpacked) >= 0

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.stream.stop_stream()
        except OSError:
            log.warning("PyAudio stream already closed.")
        finally:
            self.stream.close()
            self.pa.terminate()
            self.porcupine.delete()


class SpeechRecognizer:
    def __init__(self, mic_index: int):
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone(device_index=mic_index)
        # Optional: calibrate for ambient noise (0.5 s)
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

    # Record speech and return text; None if silence/timeout/unknown.
    def listen(
        self,
        timeout: int = LISTEN_TIMEOUT,
        phrase_limit: int = PHRASE_LIMIT,
    ) -> str | None:
        try:
            with self.mic as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit,
                )
        except sr.WaitTimeoutError:
            log.debug("Listen timeout (%s s) – no speech started", timeout)
            return None
        except OSError as e:
            log.error("Microphone I/O error: %s", e)
            return None

        try:
            return self.recognizer.recognize_google(audio, language="de-DE")
        except sr.UnknownValueError:
            log.debug("Speech unintelligible")
            return None
        except sr.RequestError as e:
            # Network or API issue – escalate to caller
            log.error("Google STT error: %s", e)
            return None


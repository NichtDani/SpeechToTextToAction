# ---------------------------
# assistant/audio.py
# Audio input, wake‑word detection (Porcupine) and speech recognition.
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


#Context‑manager wrapper around Porcupine & PyAudio.
class WakeListener(AbstractContextManager):
    def __init__(self, mic_index: int):
        self.porcupine = pvporcupine.create(
            access_key=ACCESS_KEY,
            keywords=[WAKE_KEYWORD],
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

    def pause(self):
        if self.stream.is_active():
            self.stream.stop_stream()

    def resume(self):
        if not self.stream.is_active():
            self.stream.start_stream()
    
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
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()
        self.porcupine.delete()


class SpeechRecognizer:
    def __init__(self, mic_index: int):
        self.recognizer = sr.Recognizer()
        self.mic_index = mic_index

# Record speech and return text; None if silence/timeout/unknown.
    def listen(
        self,
        timeout: int = LISTEN_TIMEOUT,
        phrase_limit: int = PHRASE_LIMIT,
    ) -> str | None:
        try:
            with sr.Microphone(device_index=self.mic_index) as source:
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_limit
                )
        except sr.WaitTimeoutError:
            log.debug("Listen timeout (%s s) – no speech started", timeout)
            return None

        try:
            return self.recognizer.recognize_google(audio, language="de-DE")
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            log.error("Google STT error: %s", e)
            return None

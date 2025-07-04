import pvporcupine
import pyaudio
import struct
import speech_recognition as sr
import pyttsx3
import webbrowser

ACCESS_KEY = "nkTVaKlJG4CNYUBk6vISKHMz9c7+K8exB8V1WkgMs+jPEVCuPSNxgA=="

# 🗣️ Text zu Sprache
def sprechen(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# 🎛️ Befehle ausführen
def befehl_verarbeiten(befehl):
    if "öffne youtube" in befehl.lower():
        sprechen("YouTube wird geöffnet")
        webbrowser.open("https://youtube.com")
    elif "stopp" in befehl.lower():
        sprechen("Beende den Bot.")
        exit()
    else:
        sprechen("Befehl nicht erkannt.")

# 🎙️ Sprachbefehl aufnehmen nach Wakeword
def sprache_zu_text(mikro_index):
    r = sr.Recognizer()
    with sr.Microphone(device_index=mikro_index) as quelle:
        print("🎤 Sprich deinen Befehl...")
        audio = r.listen(quelle)
        try:
            text = r.recognize_google(audio, language="de-DE")
            print("🗣️ Du hast gesagt:", text)
            return text
        except:
            sprechen("Ich konnte dich nicht verstehen.")
            return ""

# 🎚️ Mikrofon-Auswahl anzeigen & abfragen
def mikrofon_auswählen():
    pa = pyaudio.PyAudio()
    print("🔊 Verfügbare Mikrofone:")
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if info["maxInputChannels"] > 0:
            print(f"{i}: {info['name']}")
    pa.terminate()

    while True:
        try:
            auswahl = int(input("🎙️ Wähle ein Mikrofon (Index eingeben): "))
            return auswahl
        except ValueError:
            print("❌ Bitte eine gültige Zahl eingeben.")

# 🧠 Wakeword-Loop mit Porcupine starten
def wakeword_loop():
    mikro_index = mikrofon_auswählen()

    porcupine = pvporcupine.create(
        access_key=ACCESS_KEY,
        keywords=["jarvis"]
    )

    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        input_device_index=mikro_index,
        frames_per_buffer=porcupine.frame_length
    )

    print("👂 Warte auf Wakeword...")

    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)

            result = porcupine.process(pcm_unpacked)
            if result >= 0:
                print("🎯 Wakeword erkannt!")
                sprechen("Ich höre.")
                befehl = sprache_zu_text(mikro_index)
                if befehl:
                    befehl_verarbeiten(befehl)

    except KeyboardInterrupt:
        print("🛑 Beendet")

    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()

# ▶️ Start
if __name__ == "__main__":
    wakeword_loop()

import pvporcupine
import pyaudio
import struct
import speech_recognition as sr
import pyttsx3
import webbrowser
import os

from dotenv import load_dotenv

load_dotenv()
ACCESS_KEY = os.getenv("ACCESS_KEY")

# Text-to-speech Ausgaben
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

# Verarbeite Sprachbefehl
def process_command(command):
    if "öffne youtube" in command.lower():
        speak("YouTube wird geöffnet.")
        webbrowser.open("https://youtube.com")
    elif "stopp" in command.lower():
        speak("Der Assistent wird beendet.")
        exit()
    else:
        speak("Befehl nicht erkannt.")

# Sprachaufnahme nach dem Wakeword
def listen_for_command(mic_index):
    r = sr.Recognizer()
    with sr.Microphone(device_index=mic_index) as source:
        print("🎤 Sprich deinen Befehl...")
        audio = r.listen(source)
        print("Rohbytes:", len(audio.frame_data))
        try:
            text = r.recognize_google(audio, language="de-DE")
            print("🗣️ Du hast gesagt:", text)
            return text
        except:
            speak("Ich konnte dich nicht verstehen.")
            return ""

# Mikrofon auswählen
def select_microphone():
    pa = pyaudio.PyAudio()
    print("🔊 Verfügbare Mikrofone:")
    for i in range(pa.get_device_count()):
        info = pa.get_device_info_by_index(i)
        if info["maxInputChannels"] > 0:
            print(f"{i}: {info['name']}")
    pa.terminate()

    while True:
        try:
            selected = int(input("🎙️ Wähle ein Mikrofon (Index eingeben): "))
            return selected
        except ValueError:
            print("❌ Bitte eine gültige Zahl eingeben.")

# Wakeword-Loop starten
def wakeword_loop():
    mic_index = select_microphone()

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
        input_device_index=mic_index,
        frames_per_buffer=porcupine.frame_length
    )

    print("Warte auf Wakeword...")

    try:
        while True:
            pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm_unpacked = struct.unpack_from("h" * porcupine.frame_length, pcm)

            result = porcupine.process(pcm_unpacked)
            if result >= 0:
                print("🎯 Wakeword erkannt!")
                command = listen_for_command(mic_index)
                if command:
                    process_command(command)

    except KeyboardInterrupt:
        print("🛑 Vom Benutzer beendet.")

    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()
        
# ------------
# Startpunkt
# ------------

if __name__ == "__main__":
    wakeword_loop()
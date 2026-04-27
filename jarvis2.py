import datetime
import random
import subprocess
import sys
import unicodedata
import webbrowser

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None


class Jarvis:
    def __init__(self):
        self.engine = None
        self.voice_mode = False
        self.running = True
        self.wake_words = ("jarvis", "yarvis")
        self.listen_mode = "wake_word"
        self.recognizer = sr.Recognizer() if sr is not None else None
        self._setup_tts()

    def _setup_tts(self):
        if pyttsx3 is None:
            return
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty("rate", 170)
            self.voice_mode = True
        except Exception:
            self.engine = None
            self.voice_mode = False

    def speak(self, text: str):
        print(f"JARVIS: {text}")
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()

    def listen(self) -> str:
        if sr is None:
            return input("Tu comando > ").strip().lower()

        try:
            with sr.Microphone() as source:
                print("Escuchando...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=7)
        except sr.WaitTimeoutError:
            return ""

        try:
            text = self.recognizer.recognize_google(audio, language="es-ES")
            print(f"Tu: {text}")
            return text.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            self.speak("No puedo conectar con el servicio de voz.")
            return ""

    @staticmethod
    def normalize_text(text: str) -> str:
        normalized = unicodedata.normalize("NFD", text)
        normalized = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
        return normalized.lower().strip()

    def extract_after_wake_word(self, command: str) -> str:
        normalized = self.normalize_text(command)
        for wake_word in self.wake_words:
            if normalized.startswith(wake_word):
                return normalized[len(wake_word) :].strip(" ,.:;!-")
        return ""

    def open_notepad(self):
        if sys.platform.startswith("win"):
            subprocess.Popen(["notepad.exe"])
            self.speak("Abriendo bloc de notas.")
        else:
            self.speak("Este comando está pensado para Windows.")

    def tell_time(self):
        now = datetime.datetime.now().strftime("%H:%M")
        self.speak(f"La hora actual es {now}.")

    def tell_date(self):
        today = datetime.datetime.now().strftime("%d/%m/%Y")
        self.speak(f"Hoy es {today}.")

    def open_youtube(self):
        webbrowser.open("https://www.youtube.com")
        self.speak("Abriendo YouTube.")

    def open_google(self):
        webbrowser.open("https://www.google.com")
        self.speak("Abriendo Google.")

    def search_google(self, query: str):
        if not query:
            self.speak("Dime qué quieres buscar.")
            return
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        self.speak(f"Buscando {query} en Google.")

    def tell_joke(self):
        jokes = [
            "¿Cuál es el animal más antiguo? La cebra, porque está en blanco y negro.",
            "¿Qué le dice un jardinero a otro? Nos vemos cuando podamos.",
            "¿Por qué la computadora fue al doctor? Porque tenía un virus.",
        ]
        self.speak(random.choice(jokes))

    def help(self):
        commands = [
            "hora",
            "fecha",
            "abrir youtube",
            "abrir google",
            "abrir bloc",
            "buscar <texto>",
            "chiste",
            "escucha continua",
            "escucha por activacion",
            "salir",
        ]
        self.speak(
            "Comandos disponibles: "
            + ", ".join(commands)
            + ". En modo activacion, empieza diciendo jarvis o yarvis."
        )

    def process_command(self, command: str):
        command = self.normalize_text(command)
        if not command:
            return

        if "hora" in command:
            self.tell_time()
        elif "fecha" in command:
            self.tell_date()
        elif "abrir youtube" in command:
            self.open_youtube()
        elif "abrir google" in command:
            self.open_google()
        elif "abrir bloc" in command or "abrir notepad" in command:
            self.open_notepad()
        elif command.startswith("buscar "):
            query = command.replace("buscar ", "", 1).strip()
            self.search_google(query)
        elif "chiste" in command:
            self.tell_joke()
        elif "escucha continua" in command:
            self.listen_mode = "continuous"
            self.speak("Modo escucha continua activado.")
        elif "escucha por activacion" in command or "modo activacion" in command:
            self.listen_mode = "wake_word"
            self.speak("Modo por palabra de activacion activado.")
        elif "ayuda" in command or "comandos" in command:
            self.help()
        elif "salir" in command or "adios" in command:
            self.speak("Hasta luego. Sistema JARVIS apagado.")
            self.running = False
        else:
            self.speak("Comando no reconocido. Di ayuda para ver opciones.")

    def run(self):
        mode = "voz y texto" if self.voice_mode and sr is not None else "solo texto"
        self.speak(f"Sistema JARVIS iniciado en modo {mode}.")
        self.speak("Di jarvis o yarvis seguido del comando. Di ayuda para ver comandos.")
        while self.running:
            spoken_text = self.listen()
            if not spoken_text:
                continue

            command = spoken_text
            if self.voice_mode and sr is not None and self.listen_mode == "wake_word":
                command = self.extract_after_wake_word(spoken_text)
                if not command:
                    continue

            self.process_command(command)


if __name__ == "__main__":
    jarvis = Jarvis()
    jarvis.run()

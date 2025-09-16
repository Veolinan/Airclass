import pygame
import tempfile
import time
from gtts import gTTS
import os

# Initialize pygame mixer once
pygame.mixer.init()

def play_sound(file_path):
    """
    Plays a given .mp3 or .wav file using pygame.
    """
    try:
        if not os.path.exists(file_path):
            print(f"❌ Sound file not found: {file_path}")
            return

        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    except Exception as e:
        print("❌ Error playing sound:", e)

def speak_word(word, lang="en"):
    """
    Speaks the given word using gTTS and pygame.
    """
    try:
        tts = gTTS(text=word, lang=lang)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            pygame.mixer.music.load(fp.name)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            os.remove(fp.name)
    except Exception as e:
        print("❌ Error speaking word:", e)

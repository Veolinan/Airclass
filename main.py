# File: main.py
import os
import sys
import time
import pygame
import cv2
import numpy as np

# ensure local packages importable when running py main.py
sys.path.append(os.path.dirname(__file__))

from utils.graphics import Button, draw_text_center
from utils.hand_tracker import HandTracker
from utils.sound import SoundManager
from modules import counting, numbers, shapes, sorting

# Constants
WIDTH, HEIGHT = 1280, 720
FPS = 30

# Init
pygame.init()
pygame.mixer.init()  # safe even if audio device is missing on some systems
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("AirClass — Touchless Learning")
clock = pygame.time.Clock()

# Sound manager (silent fallback if files missing)
sound = SoundManager(assets_dir=os.path.join(os.path.dirname(__file__), "assets", "sounds"))
sound.load("click", "click.wav")
sound.load("success", "success.wav")
sound.load("error", "error.wav")
# try play theme, but silently continue if missing
sound.play_music("theme.mp3")

# Camera + hand tracker (shared)
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
time.sleep(0.2)
if not cap.isOpened():
    print("[Camera Warning] Could not open camera. App will run with blank background.")
hand_tracker = HandTracker(max_num_hands=1)

# UI buttons (rect, text, base_color)
WHITE = (255, 255, 255)
BLUE = (40, 140, 255)
RED = (210, 60, 60)
buttons = [
    Button((WIDTH // 2 - 220, 160, 440, 100), "Counting", BLUE),
    Button((WIDTH // 2 - 220, 290, 440, 100), "Sorting", BLUE),
    Button((WIDTH // 2 - 220, 420, 440, 100), "Numbers", BLUE),
    Button((WIDTH // 2 - 220, 550, 440, 100), "Shapes", BLUE),
    Button((WIDTH // 2 - 120, 640, 240, 60), "Exit", RED),
]


def get_frame():
    """Return (frame_bgr) or None. Frame is not flipped here."""
    if not cap.isOpened():
        return None
    ret, frame = cap.read()
    if not ret:
        return None
    # mirror for intuitive interaction
    frame = cv2.flip(frame, 1)
    # ensure expected size
    frame = cv2.resize(frame, (WIDTH, HEIGHT))
    return frame


def frame_to_surface(frame_bgr, alpha=None):
    """Convert BGR OpenCV frame to pygame surface. Optionally set alpha (0-255)."""
    if frame_bgr is None:
        surf = pygame.Surface((WIDTH, HEIGHT))
        surf.fill((0, 0, 0))
        return surf
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    surf = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
    if alpha is not None:
        surf.set_alpha(alpha)
    return surf


def main_menu():
    running = True
    hover_pointer = None  # pixel (x,y) of index fingertip when present
    pointing_active = False

    while running:
        clock.tick(FPS)

        # --- camera background ---
        frame = get_frame()
        if frame is not None:
            # process hand (returns dict)
            hand_data = hand_tracker.process(frame)
            # we draw landmarks later on top; keep 'frame' as base
        else:
            # blank frame if no camera
            hand_data = {'frame': None, 'index_pos': None, 'pinch': False, 'landmarks': None}

        # base background
        bg = frame_to_surface(hand_data['frame'])
        screen.blit(bg, (0, 0))

        # UI title
        draw_text_center(screen, "AirClass — Touchless Learning", 48, WHITE, (WIDTH // 2, 60))

        # pointer state from hand_data
        idx = hand_data.get('index_pos')
        pinch = hand_data.get('pinch', False)
        # pointing_active: index present and not pinching
        pointing_active = (idx is not None) and (not pinch)
        hover_pointer = idx

        # draw buttons and handle point-and-hold selection
        for b in buttons:
            progress = b.update_hover(hover_pointer, pointing_active)
            b.draw(screen, hover_progress=progress)
            if progress >= 1.0:
                sound.play("click")
                # route
                if b.text == "Counting":
                    counting.run(screen, clock, cap, hand_tracker, sound)
                elif b.text == "Sorting":
                    sorting.run(screen, clock, cap, hand_tracker, sound)
                elif b.text == "Numbers":
                    numbers.run(screen, clock, cap, hand_tracker, sound)
                elif b.text == "Shapes":
                    shapes.run(screen, clock, cap, hand_tracker, sound)
                elif b.text == "Exit":
                    running = False
                # reset hovers so user doesn't immediately re-enter
                for bb in buttons:
                    bb.reset_hover()
                break

        # draw hand overlay ON TOP of UI (ensure visible)
        if hand_data['frame'] is not None:
            # draw landmarks onto a copy of frame so we don't modify original
            overlay_frame = hand_data['frame'].copy()
            hand_tracker.draw_hand(overlay_frame, landmark_color=(0, 255, 0), connections_color=(0, 200, 0), thickness=2)
            overlay = frame_to_surface(overlay_frame, alpha=220)  # slightly translucent so UI still readable
            screen.blit(overlay, (0, 0))

        # events (also allow mouse click fallback)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mp = pygame.mouse.get_pos()
                # allow clicking menu with mouse as fallback
                for b in buttons:
                    if b.is_hovered(mp):
                        sound.play("click")
                        if b.text == "Counting":
                            counting.run(screen, clock, cap, hand_tracker, sound)
                        elif b.text == "Sorting":
                            sorting.run(screen, clock, cap, hand_tracker, sound)
                        elif b.text == "Numbers":
                            numbers.run(screen, clock, cap, hand_tracker, sound)
                        elif b.text == "Shapes":
                            shapes.run(screen, clock, cap, hand_tracker, sound)
                        elif b.text == "Exit":
                            running = False
                        for bb in buttons:
                            bb.reset_hover()
                        break

        pygame.display.flip()

    # cleanup
    cap.release()
    pygame.quit()


if __name__ == "__main__":
    try:
        main_menu()
    except Exception as e:
        print("Fatal error:", e)
        cap.release()
        pygame.quit()
        raise

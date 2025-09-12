# File: modules/numbers.py
import cv2
import random
import time
import pygame
from utils.graphics import Button, draw_text_center, draw_star

WHITE = (255, 255, 255)


# --------------------------
# Counting Activity
# --------------------------
def activity_counting(screen, clock, cap, hand_tracker, sound):
    W, H = screen.get_size()
    back_btn = Button((20, 20, 160, 70), "Back", (120, 120, 120))
    prev_pinch = False
    flash_msg = None
    flash_time = 0

    def make_scene():
        count = random.randint(2, 7)
        positions = [(random.randint(120, W-120), random.randint(120, H-260)) for _ in range(count)]
        return {"count": count, "positions": positions}

    scene = make_scene()
    num_buttons = [Button((100 + (i-1)*140, H-120, 120, 90), str(i), (90, 180, 220)) for i in range(1, 9)]

    while True:
        clock.tick(30)
        ret, frame = cap.read()
        if not ret:
            hand = {"frame": None, "index_pos": None, "pinch": False}
        else:
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (W, H))
            hand = hand_tracker.process(frame)

        # camera bg
        if hand["frame"] is None:
            screen.fill((0, 0, 0))
        else:
            surf = cv2.cvtColor(hand["frame"], cv2.COLOR_BGR2RGB)
            surf = pygame.surfarray.make_surface(surf.swapaxes(0, 1))
            screen.blit(surf, (0, 0))

        draw_text_center(screen, "How many items?", 44, WHITE, (W//2, 60))

        # items
        for pos in scene["positions"]:
            pygame.draw.circle(screen, (0, 160, 220), pos, 36)
            pygame.draw.circle(screen, (255, 255, 255), pos, 36, 3)

        # buttons
        p = hand.get("index_pos")
        for b in num_buttons + [back_btn]:
            prog = b.update_hover(p, pointing_active=(p and not hand.get("pinch", False)))
            b.draw(screen, hover_progress=prog)

        # overlay hand
        if hand["frame"] is not None:
            overlay_frame = hand["frame"].copy()
            hand_tracker.draw_hand(overlay_frame)
            overlay = pygame.surfarray.make_surface(
                cv2.cvtColor(overlay_frame, cv2.COLOR_BGR2RGB).swapaxes(0, 1)
            )
            overlay.set_alpha(230)
            screen.blit(overlay, (0, 0))

        pinch = hand.get("pinch", False)
        if pinch and not prev_pinch:
            if back_btn.rect.collidepoint(p or (-1, -1)):
                sound.play("click")
                return
            for i, b in enumerate(num_buttons):
                if b.rect.collidepoint(p or (-1, -1)):
                    chosen = i + 1
                    if chosen == scene["count"]:
                        sound.play("success")
                        flash_msg = "Correct!"
                        flash_time = time.time()
                        for _ in range(5):
                            draw_star(screen, (W//2, H//2))
                            pygame.display.flip()
                            pygame.time.delay(70)
                        scene = make_scene()
                    else:
                        sound.play("error")
                        flash_msg = "Try again!"
                        flash_time = time.time()
                    break
        prev_pinch = pinch

        if flash_msg and time.time() - flash_time < 1.5:
            draw_text_center(screen, flash_msg, 48, (200, 255, 200), (W//2, H//2))
        elif flash_msg:
            flash_msg = None

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if back_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    return

        pygame.display.flip()


# --------------------------
# Simple Arithmetic Activities
# --------------------------
def activity_arithmetic(screen, clock, cap, hand_tracker, sound, mode="add"):
    W, H = screen.get_size()
    back_btn = Button((20, 20, 160, 70), "Back", (120, 120, 120))
    prev_pinch = False
    flash = None
    flash_time = 0

    def make_question():
        a, b = random.randint(1, 9), random.randint(1, 9)
        if mode == "add":
            return f"{a} + {b} = ?", a+b
        elif mode == "sub":
            a, b = max(a, b), min(a, b)
            return f"{a} - {b} = ?", a-b

    q_text, answer = make_question()
    num_buttons = [Button((100 + (i-1)*140, H-120, 120, 90), str(i), (90, 200, 160)) for i in range(0, 10)]

    while True:
        clock.tick(30)
        ret, frame = cap.read()
        if not ret:
            hand = {"frame": None, "index_pos": None, "pinch": False}
        else:
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (W, H))
            hand = hand_tracker.process(frame)

        # bg
        if hand["frame"] is None:
            screen.fill((0, 0, 0))
        else:
            surf = cv2.cvtColor(hand["frame"], cv2.COLOR_BGR2RGB)
            surf = pygame.surfarray.make_surface(surf.swapaxes(0, 1))
            screen.blit(surf, (0, 0))

        draw_text_center(screen, q_text, 56, WHITE, (W//2, H//3))

        p = hand.get("index_pos")
        for b in num_buttons + [back_btn]:
            prog = b.update_hover(p, pointing_active=(p and not hand.get("pinch", False)))
            b.draw(screen, hover_progress=prog)

        # overlay hand
        if hand["frame"] is not None:
            overlay_frame = hand["frame"].copy()
            hand_tracker.draw_hand(overlay_frame)
            overlay = pygame.surfarray.make_surface(
                cv2.cvtColor(overlay_frame, cv2.COLOR_BGR2RGB).swapaxes(0, 1)
            )
            overlay.set_alpha(230)
            screen.blit(overlay, (0, 0))

        pinch = hand.get("pinch", False)
        if pinch and not prev_pinch:
            if back_btn.rect.collidepoint(p or (-1, -1)):
                return
            for i, b in enumerate(num_buttons):
                if b.rect.collidepoint(p or (-1, -1)):
                    chosen = int(b.text)
                    if chosen == answer:
                        sound.play("success")
                        flash = "Correct!"
                        flash_time = time.time()
                        for _ in range(5):
                            draw_star(screen, (W//2, H//2))
                            pygame.display.flip()
                            pygame.time.delay(70)
                        q_text, answer = make_question()
                    else:
                        sound.play("error")
                        flash = "Wrong!"
                        flash_time = time.time()
        prev_pinch = pinch

        if flash and time.time() - flash_time < 1.5:
            draw_text_center(screen, flash, 48, (200, 255, 200), (W//2, H//2))
        elif flash:
            flash = None

        pygame.display.flip()


# --------------------------
# Odd/Even Activity
# --------------------------
def activity_odd_even(screen, clock, cap, hand_tracker, sound):
    return activity_arithmetic(screen, clock, cap, hand_tracker, sound, mode="odd_even")  # placeholder


# --------------------------
# Fill in Missing Number Activity (5th)
# --------------------------
def activity_missing(screen, clock, cap, hand_tracker, sound):
    W, H = screen.get_size()
    back_btn = Button((20, 20, 160, 70), "Back", (120, 120, 120))
    prev_pinch = False

    def make_question():
        seq_start = random.randint(1, 5)
        seq = list(range(seq_start, seq_start+5))
        missing_index = random.randint(0, 4)
        answer = seq[missing_index]
        seq[missing_index] = "?"
        return seq, answer

    seq, answer = make_question()
    num_buttons = [Button((100 + i*140, H-120, 120, 90), str(i), (200, 160, 100)) for i in range(1, 11)]
    flash, flash_time = None, 0

    while True:
        clock.tick(30)
        ret, frame = cap.read()
        if not ret:
            hand = {"frame": None, "index_pos": None, "pinch": False}
        else:
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (W, H))
            hand = hand_tracker.process(frame)

        if hand["frame"] is None:
            screen.fill((0, 0, 0))
        else:
            surf = cv2.cvtColor(hand["frame"], cv2.COLOR_BGR2RGB)
            surf = pygame.surfarray.make_surface(surf.swapaxes(0, 1))
            screen.blit(surf, (0, 0))

        draw_text_center(screen, "Fill the missing number:", 44, WHITE, (W//2, 60))
        font = pygame.font.Font(None, 72)
        seq_str = "   ".join(str(n) for n in seq)
        txt = font.render(seq_str, True, (255, 255, 0))
        screen.blit(txt, (W//2 - txt.get_width()//2, H//3))

        p = hand.get("index_pos")
        for b in num_buttons + [back_btn]:
            prog = b.update_hover(p, pointing_active=(p and not hand.get("pinch", False)))
            b.draw(screen, hover_progress=prog)

        if hand["frame"] is not None:
            overlay_frame = hand["frame"].copy()
            hand_tracker.draw_hand(overlay_frame)
            overlay = pygame.surfarray.make_surface(
                cv2.cvtColor(overlay_frame, cv2.COLOR_BGR2RGB).swapaxes(0, 1)
            )
            overlay.set_alpha(230)
            screen.blit(overlay, (0, 0))

        pinch = hand.get("pinch", False)
        if pinch and not prev_pinch:
            if back_btn.rect.collidepoint(p or (-1, -1)):
                return
            for b in num_buttons:
                if b.rect.collidepoint(p or (-1, -1)):
                    chosen = int(b.text)
                    if chosen == answer:
                        sound.play("success")
                        flash = "Correct!"
                        flash_time = time.time()
                        for _ in range(5):
                            draw_star(screen, (W//2, H//2))
                            pygame.display.flip()
                            pygame.time.delay(70)
                        seq, answer = make_question()
                    else:
                        sound.play("error")
                        flash = "Wrong!"
                        flash_time = time.time()
        prev_pinch = pinch

        if flash and time.time() - flash_time < 1.5:
            draw_text_center(screen, flash, 48, (200, 255, 200), (W//2, H-200))
        elif flash:
            flash = None

        pygame.display.flip()


# --------------------------
# Numbers Main Menu
# --------------------------
def run(screen, clock, cap, hand_tracker, sound):
    W, H = screen.get_size()
    back_btn = Button((20, 20, 160, 70), "Back", (120, 120, 120))

    menu_buttons = [
        Button((W//2 - 150, 150, 300, 80), "Counting", (90, 180, 220)),
        Button((W//2 - 150, 250, 300, 80), "Addition", (100, 200, 180)),
        Button((W//2 - 150, 350, 300, 80), "Subtraction", (180, 160, 220)),
        Button((W//2 - 150, 450, 300, 80), "Odd/Even", (220, 180, 120)),
        Button((W//2 - 150, 550, 300, 80), "Missing Number", (200, 160, 100)),
    ]
    prev_pinch = False

    while True:
        clock.tick(30)
        ret, frame = cap.read()
        if not ret:
            hand = {"frame": None, "index_pos": None, "pinch": False}
        else:
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (W, H))
            hand = hand_tracker.process(frame)

        if hand["frame"] is None:
            screen.fill((30, 30, 30))
        else:
            surf = cv2.cvtColor(hand["frame"], cv2.COLOR_BGR2RGB)
            surf = pygame.surfarray.make_surface(surf.swapaxes(0, 1))
            screen.blit(surf, (0, 0))

        draw_text_center(screen, "Numbers Activities", 56, WHITE, (W//2, 60))

        p = hand.get("index_pos")
        for b in menu_buttons + [back_btn]:
            prog = b.update_hover(p, pointing_active=(p and not hand.get("pinch", False)))
            b.draw(screen, hover_progress=prog)

        if hand["frame"] is not None:
            overlay_frame = hand["frame"].copy()
            hand_tracker.draw_hand(overlay_frame)
            overlay = pygame.surfarray.make_surface(
                cv2.cvtColor(overlay_frame, cv2.COLOR_BGR2RGB).swapaxes(0, 1)
            )
            overlay.set_alpha(230)
            screen.blit(overlay, (0, 0))

        pinch = hand.get("pinch", False)
        if pinch and not prev_pinch:
            if back_btn.rect.collidepoint(p or (-1, -1)):
                return
            for b in menu_buttons:
                if b.rect.collidepoint(p or (-1, -1)):
                    sound.play("click")
                    if b.text == "Counting":
                        activity_counting(screen, clock, cap, hand_tracker, sound)
                    elif b.text == "Addition":
                        activity_arithmetic(screen, clock, cap, hand_tracker, sound, mode="add")
                    elif b.text == "Subtraction":
                        activity_arithmetic(screen, clock, cap, hand_tracker, sound, mode="sub")
                    elif b.text == "Odd/Even":
                        activity_odd_even(screen, clock, cap, hand_tracker, sound)
                    elif b.text == "Missing Number":
                        activity_missing(screen, clock, cap, hand_tracker, sound)
        prev_pinch = pinch

        pygame.display.flip()

import cv2
import random
import time
import math
import pygame
from utils.graphics import Button, draw_text_center, draw_star

WHITE = (255, 255, 255)
SHAPES = ["circle", "square", "triangle", "star"]


def draw_shape_on_surf(screen, shape, center, size=100, color=(60, 170, 210)):
    """Draws a geometric shape at a given position."""
    x, y = center
    if shape == "circle":
        pygame.draw.circle(screen, color, center, size // 2)
    elif shape == "square":
        pygame.draw.rect(
            screen, color, (x - size // 2, y - size // 2, size, size), border_radius=12
        )
    elif shape == "triangle":
        pts = [(x, y - size // 2), (x - size // 2, y + size // 2), (x + size // 2, y + size // 2)]
        pygame.draw.polygon(screen, color, pts)
    elif shape == "star":
        points = []
        for i in range(5):
            angle = i * (2 * math.pi / 5) - math.pi / 2
            points.append((x + (size // 2) * math.cos(angle), y + (size // 2) * math.sin(angle)))
            angle2 = angle + math.pi / 5
            points.append((x + (size // 4) * math.cos(angle2), y + (size // 4) * math.sin(angle2)))
        pygame.draw.polygon(screen, color, points)


def make_scene(W, H):
    """Generates a new random set of shapes with one as target."""
    choices = random.sample(SHAPES, 4)
    positions = [(random.randint(140, W - 140), random.randint(120, H - 220)) for _ in range(4)]
    target_idx = random.randrange(4)
    target = choices[target_idx]
    return {"choices": choices, "positions": positions, "target": target}


def run(screen, clock, cap, hand_tracker, sound):
    """Shapes learning module."""
    W, H = screen.get_size()
    back_btn = Button((20, 20, 160, 70), "Back", (120, 120, 120))

    prev_pinch = False
    flash_msg = None
    flash_time = 0
    scene = make_scene(W, H)

    while True:
        clock.tick(30)

        # Camera frame
        ret, frame = cap.read()
        if not ret:
            hand = {"frame": None, "index_pos": None, "pinch": False}
        else:
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (W, H))
            hand = hand_tracker.process(frame)

        # Background (camera or black fallback)
        if hand["frame"] is None:
            screen.fill((0, 0, 0))
        else:
            surf = cv2.cvtColor(hand["frame"], cv2.COLOR_BGR2RGB)
            surf = pygame.surfarray.make_surface(surf.swapaxes(0, 1))
            screen.blit(surf, (0, 0))

        # Title
        draw_text_center(screen, f"Tap the {scene['target']}", 44, WHITE, (W // 2, 60))

        # Draw shapes
        for i, shape in enumerate(scene["choices"]):
            pos = scene["positions"][i]
            draw_shape_on_surf(screen, shape, pos, size=110)
            # Debug index label
            font = pygame.font.Font(None, 28)
            txt = font.render(str(i + 1), True, (255, 255, 255))
            screen.blit(txt, (pos[0] - 10, pos[1] + 50))

        # Draw buttons
        index_pos = hand.get("index_pos")
        for b in [back_btn]:
            prog = b.update_hover(
                index_pos, pointing_active=(index_pos is not None and not hand.get("pinch", False))
            )
            b.draw(screen, hover_progress=prog)

        # Draw overlay hand on top of UI
        if hand["frame"] is not None:
            overlay_frame = hand["frame"].copy()
            hand_tracker.draw_hand(overlay_frame)
            overlay = pygame.surfarray.make_surface(
                cv2.cvtColor(overlay_frame, cv2.COLOR_BGR2RGB).swapaxes(0, 1)
            )
            overlay.set_alpha(220)
            screen.blit(overlay, (0, 0))

        # Pinch selection
        pinch = hand.get("pinch", False)
        if pinch and not prev_pinch:
            # Back button
            if back_btn.rect.collidepoint(index_pos if index_pos else (-1, -1)):
                sound.play("click")
                return

            # Shape check
            for i, pos in enumerate(scene["positions"]):
                x, y = pos
                if index_pos and (x - 60 <= index_pos[0] <= x + 60 and y - 60 <= index_pos[1] <= y + 60):
                    if scene["choices"][i] == scene["target"]:
                        sound.play("success")
                        flash_msg = "Well done!"
                        flash_time = time.time()

                        # Celebration stars
                        for _ in range(5):
                            draw_star(screen, (W // 2, H // 2))
                            pygame.display.flip()
                            pygame.time.delay(80)

                        scene = make_scene(W, H)
                    else:
                        sound.play("error")
                        flash_msg = "Try again!"
                        flash_time = time.time()
                    break

        prev_pinch = pinch

        # Flash feedback
        if flash_msg and time.time() - flash_time < 1.5:
            draw_text_center(screen, flash_msg, 44, (200, 255, 200), (W // 2, H // 2))
        elif flash_msg:
            flash_msg = None

        # Events
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if back_btn.rect.collidepoint(pygame.mouse.get_pos()):
                    sound.play("click")
                    return

        pygame.display.flip()

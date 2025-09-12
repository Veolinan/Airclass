import pygame
import cv2
import random
from utils.graphics import draw_text_center, Button

def run(screen, clock, cap, hand_tracker, sound):
    """
    Counting module — shows random objects to count.
    """
    WHITE = (255, 255, 255)
    BLUE = (50, 150, 255)

    # Back button
    back_button = Button("Back", (20, 20, 150, 60), (200, 50, 50))

    # Example objects: simple colored circles
    num_items = random.randint(2, 6)
    positions = [(random.randint(100, 800), random.randint(150, 600)) for _ in range(num_items)]

    running = True
    while running:
        ret, frame = cap.read()
        if not ret:
            continue
        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cam_surface = pygame.surfarray.make_surface(frame_rgb.swapaxes(0, 1))
        screen.blit(cam_surface, (0, 0))

        # Process hand
        info = hand_tracker.process(frame)
        hand_tracker.draw_hand(frame)  # outline on top

        # Overlay UI
        draw_text_center(screen, f"Count the circles! ({num_items})", 40, WHITE, (480, 50))
        for pos in positions:
            pygame.draw.circle(screen, BLUE, pos, 30)

        mouse_pos = pygame.mouse.get_pos()
        back_button.draw(screen, mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.is_hovered(mouse_pos):
                    sound.play_sound("assets/sounds/back.wav")
                    running = False

        pygame.display.flip()
        clock.tick(30)

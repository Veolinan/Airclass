# File: utils/graphics.py
import pygame
import time
import math

pygame.font.init()
DEFAULT_FONT_NAME = None  # use default system font

class Button:
    """
    Button(rect, text, color)
    - rect: (x,y,w,h)
    - supports point-and-hold via update_hover(pointer_pos, pointing_active)
    """
    def __init__(self, rect, text, color=(0,150,255), text_color=(255,255,255), hold_time=1.0):
        self.rect = pygame.Rect(*rect)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = pygame.font.Font(DEFAULT_FONT_NAME, 36)
        self.hover_start = None
        self.hold_time = hold_time
        self.last_progress = 0.0

    def draw(self, screen, hover_progress=0.0):
        # background
        pygame.draw.rect(screen, self.color, self.rect, border_radius=16)
        # border
        pygame.draw.rect(screen, (255,255,255), self.rect, 3, border_radius=16)
        # label
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        # progress ring (top-right)
        if hover_progress > 0:
            center = (self.rect.right - 30, self.rect.top + 30)
            radius = 20
            thickness = 5
            # background circle
            pygame.draw.circle(screen, (100,100,100), center, radius, thickness)
            # progress arc (draw as many small lines)
            steps = int(360 * hover_progress / 4)  # coarse
            for a in range(0, int(360*hover_progress), 4):
                theta1 = math.radians(a - 90)
                p1 = (int(center[0] + radius * math.cos(theta1)), int(center[1] + radius * math.sin(theta1)))
                theta2 = math.radians(a+3 - 90)
                p2 = (int(center[0] + radius * math.cos(theta2)), int(center[1] + radius * math.sin(theta2)))
                pygame.draw.line(screen, (255,255,255), p1, p2, thickness)

    def update_hover(self, pointer_pos, pointing_active):
        """
        pointer_pos: (x,y) or None
        pointing_active: True if the user is pointing (index present & not pinching)
        Returns hover_progress in [0,1].
        """
        inside = pointer_pos is not None and self.rect.collidepoint(pointer_pos) and pointing_active
        if inside:
            if self.hover_start is None:
                self.hover_start = time.time()
            elapsed = time.time() - self.hover_start
            progress = min(1.0, elapsed / self.hold_time)
            self.last_progress = progress
            return progress
        else:
            self.hover_start = None
            self.last_progress = 0.0
            return 0.0

    def reset_hover(self):
        self.hover_start = None
        self.last_progress = 0.0

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


def draw_text_center(screen, text, size, color, pos):
    font = pygame.font.Font(DEFAULT_FONT_NAME, size)
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=pos)
    screen.blit(surf, rect)


def draw_star(screen, pos, color=(255,215,0), radius=22):
    # simple star-like polygon
    points = []
    for i in range(5):
        angle = i * (2*math.pi/5) - math.pi/2
        points.append((pos[0] + radius * math.cos(angle), pos[1] + radius * math.sin(angle)))
        angle2 = angle + math.pi/5
        points.append((pos[0] + (radius/2) * math.cos(angle2), pos[1] + (radius/2) * math.sin(angle2)))
    pygame.draw.polygon(screen, color, points)

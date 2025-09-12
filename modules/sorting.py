# File: modules/sorting.py
import cv2
import random
import time
from utils.graphics import Button, draw_text_center, draw_star

WHITE = (255,255,255)

FRUITS = [
    ("Apple",(220,60,60)),
    ("Banana",(240,200,40)),
    ("Grape",(140,60,200))
]

def run(screen, clock, cap, hand_tracker, sound):
    W,H = screen.get_size()
    back_btn = Button((20,20,160,70), "Back", (120,120,120))
    prev_pinch = False
    grabbed = None
    placed = set()
    last_feedback = None
    fb_time = 0

    def make_scene():
        bins = random.sample(FRUITS, 2)
        items = []
        for i in range(5):
            name, color = random.choice(FRUITS)
            items.append({'name':name,'color':color,'pos':[random.randint(140,W-140), random.randint(120,H-260)], 'size':70})
        return {'bins':bins, 'items':items}

    scene = make_scene()

    left_bin_pos = (80, H-180)
    right_bin_pos = (W-280, H-180)
    bin_w, bin_h = 200, 140

    while True:
        clock.tick(30)
        ret, frame = cap.read()
        if not ret:
            hand={'frame':None,'index_pos':None,'pinch':False}
        else:
            frame = cv2.flip(frame,1)
            frame = cv2.resize(frame,(W,H))
            hand = hand_tracker.process(frame)

        # background
        if hand['frame'] is None:
            screen.fill((0,0,0))
        else:
            surf = cv2.cvtColor(hand['frame'], cv2.COLOR_BGR2RGB)
            surf = pygame.surfarray.make_surface(surf.swapaxes(0,1))
            screen.blit(surf, (0,0))

        draw_text_center(screen, "Sort fruits into bins", 44, WHITE, (W//2, 60))

        # bins
        cv2_rect_left = pygame.Rect(left_bin_pos[0], left_bin_pos[1], bin_w, bin_h)
        cv2.draw = None  # no-op to avoid accidental use

        pygame.draw.rect(screen, scene['bins'][0][1], (left_bin_pos[0], left_bin_pos[1], bin_w, bin_h))
        pygame.draw.rect(screen, scene['bins'][1][1], (right_bin_pos[0], right_bin_pos[1], bin_w, bin_h))
        font = pygame.font.Font(None, 32)
        txt1 = font.render(scene['bins'][0][0], True, (255,255,255))
        txt2 = font.render(scene['bins'][1][0], True, (255,255,255))
        screen.blit(txt1, (left_bin_pos[0]+20, left_bin_pos[1]+60))
        screen.blit(txt2, (right_bin_pos[0]+20, right_bin_pos[1]+60))

        # draw items
        for idx,it in enumerate(scene['items']):
            if idx in placed: continue
            x,y = int(it['pos'][0]), int(it['pos'][1])
            s = it['size']
            pygame.draw.rect(screen, it['color'], (x-s//2,y-s//2,s,s), border_radius=10)
            label = font.render(it['name'][0], True, (255,255,255))
            screen.blit(label, (x-10,y-8))

        # back
        p = hand.get('index_pos')
        back_prog = back_btn.update_hover(p, pointing_active=(p is not None and not hand.get('pinch', False)))
        back_btn.draw(screen, hover_progress=back_prog)

        # overlay hand
        if hand['frame'] is not None:
            overlay_frame = hand['frame'].copy()
            hand_tracker.draw_hand(overlay_frame)
            overlay = pygame.surfarray.make_surface(cv2.cvtColor(overlay_frame, cv2.COLOR_BGR2RGB).swapaxes(0,1))
            overlay.set_alpha(230)
            screen.blit(overlay,(0,0))

        # handle pinch/grab logic (simple)
        pinch = hand.get('pinch', False)
        if pinch and not prev_pinch:
            # start grab: find touched fruit
            for idx,it in enumerate(scene['items']):
                if idx in placed: continue
                x,y = int(it['pos'][0]), int(it['pos'][1])
                if p and (x-40 <= p[0] <= x+40 and y-40 <= p[1] <= y+40):
                    grabbed = idx
                    sound.play("click")
                    break
        elif pinch and prev_pinch and grabbed is not None:
            # move grabbed with finger
            scene['items'][grabbed]['pos'][0] = p[0]
            scene['items'][grabbed]['pos'][1] = p[1]
        elif (not pinch) and prev_pinch and grabbed is not None:
            # released: check bins
            fx, fy = scene['items'][grabbed]['pos']
            # left bin
            if left_bin_pos[0] <= fx <= left_bin_pos[0]+bin_w and left_bin_pos[1] <= fy <= left_bin_pos[1]+bin_h:
                target = scene['bins'][0][0]
                if scene['items'][grabbed]['name'] == target:
                    placed.add(grabbed)
                    sound.play("success")
                    last_feedback = "Great!"
                    fb_time = time.time()
                else:
                    sound.play("error")
                    last_feedback = "Wrong!"
                    fb_time = time.time()
            elif right_bin_pos[0] <= fx <= right_bin_pos[0]+bin_w and right_bin_pos[1] <= fy <= right_bin_pos[1]+bin_h:
                target = scene['bins'][1][0]
                if scene['items'][grabbed]['name'] == target:
                    placed.add(grabbed)
                    sound.play("success")
                    last_feedback = "Great!"
                    fb_time = time.time()
                else:
                    sound.play("error")
                    last_feedback = "Wrong!"
                    fb_time = time.time()
            grabbed = None
            if len(placed) == len(scene['items']):
                # win -> celebrate and regen
                for _ in range(6):
                    draw_star(screen, (W//2, H//2))
                    pygame.display.flip()
                    pygame.time.delay(60)
                scene = make_scene()
                placed = set()

        prev_pinch = pinch

        # feedback text
        if 'last_feedback' in locals() and time.time() - fb_time < 1.6:
            draw_text_center(screen, last_feedback, 44, (200,255,200), (W//2, H//2))
        elif 'last_feedback' in locals():
            del last_feedback

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                mp = pygame.mouse.get_pos()
                if back_btn.rect.collidepoint(mp):
                    return

        pygame.display.flip()

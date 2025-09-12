import cv2
import random
import time
from modules.sound_player import play_sound

def run_addition(cap, tracker):
    w, h = 640, 480
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Generate a simple addition problem
    a = random.randint(1, 9)
    b = random.randint(1, 9)
    correct = a + b
    options = [correct]
    while len(options) < 4:
        wrong = random.randint(2, 18)
        if wrong != correct and wrong not in options:
            options.append(wrong)
    random.shuffle(options)

    # Layout option buttons
    option_boxes = []
    spacing = 120
    for i, opt in enumerate(options):
        x = 80 + i * spacing
        y = h // 2
        option_boxes.append((opt, (x, y, 100, 100)))

    # Back button
    back_btn = (w - 130, 20, 100, 60)

    selected = None
    result = ""
    result_time = 0
    hold_start = None
    hold_target = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (w, h))
        landmarks = tracker.get_landmarks(frame)

        # === UI ===
        cv2.putText(frame, f"What is {a} + {b}?", (30, 70), font, 1.5, (0, 120, 255), 4)

        # Draw answer options
        for val, (x, y, bw, bh) in option_boxes:
            cv2.rectangle(frame, (x, y), (x + bw, y + bh), (255, 230, 180), -1)
            cv2.putText(frame, str(val), (x + 20, y + 65), font, 2, (0, 0, 0), 4)

        # Draw BACK
        bx, by, bw, bh = back_btn
        cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (255, 255, 255), -1)
        cv2.putText(frame, "BACK", (bx + 10, by + 40), font, 1, (0, 0, 255), 2)

        # Result feedback
        if result and time.time() - result_time < 2:
            color = (0, 255, 0) if result == "Correct!" else (0, 0, 255)
            cv2.putText(frame, result, (200, 430), font, 1.5, color, 4)
        elif result == "Correct!" and time.time() - result_time >= 2:
            play_sound("assets/sounds/well_done.mp3")
            break

        # === Gesture logic ===
        if landmarks:
            x1, y1 = landmarks[4]
            x2, y2 = landmarks[8]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            dist = ((x1 - x2)**2 + (y1 - y2)**2) ** 0.5

            hovering = None
            # Check if over a button
            for val, (x, y, bw, bh) in option_boxes + [("BACK", back_btn)]:
                if x < cx < x + bw and y < cy < y + bh:
                    hovering = val
                    break

            if dist < 40 and hovering:
                if hold_target != hovering:
                    hold_start = time.time()
                    hold_target = hovering

                # Draw hold progress circle
                hold_duration = 4  # seconds
                elapsed = time.time() - hold_start
                progress = min(elapsed / hold_duration, 1)
                cv2.ellipse(frame, (cx, cy), (40, 40), -90, 0, progress * 360, (0, 255, 0), 5)

                if progress == 1:
                    if hovering == "BACK":
                        play_sound("assets/sounds/welcome.mp3")
                        return
                    elif isinstance(hovering, int):
                        if hovering == correct:
                            play_sound("assets/sounds/correct.mp3")
                            result = "Correct!"
                        else:
                            play_sound("assets/sounds/wrong.mp3")
                            result = "Wrong!"
                        result_time = time.time()
                        hold_start = None
                        hold_target = None
            else:
                hold_start = None
                hold_target = None

        tracker.draw_hand(frame)
        cv2.imshow("Addition", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    try:
        cv2.destroyWindow("Addition")
    except:
        pass

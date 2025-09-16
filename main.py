import cv2
import time
from modules.hand_tracker import HandTracker
from modules.menu import Menu
from modules.sound_player import play_sound

# 🎓 Lesson Modules
from modules.shapes_colors import run_shapes_colors
from modules.numbers.numbers import run_numbers      # ✅ Submenu for Numbers
from modules.numbers.counting import run_counting    # ✅ Renamed from run_counting_game
from modules.spellings import run_spellings
from modules.drawing import run_drawing

# 🟨 Setup Camera & Hand Tracker
cap = cv2.VideoCapture(0)
success, frame = cap.read()
if not success:
    print("❌ Failed to grab frame on startup.")
    exit()

h, w = frame.shape[:2]
tracker = HandTracker()

# 🧡 Main Menu Items
menu_labels = [
    "Shapes & Colors",
    "Numbers",
    "Counting",
    "Spellings",
    "Drawing",
    "Quit"
]
menu = Menu(menu_labels, w, h)

# 🟧 Main Loop
while True:
    success, frame = cap.read()
    if not success:
        print("❌ Failed to grab frame")
        break

    frame = cv2.flip(frame, 1)
    landmarks = tracker.get_landmarks(frame)

    # 🎨 Draw Menu
    menu.draw(frame)

    # ✋ Check Pinch-Hold Selection
    if landmarks and len(landmarks) >= 9:
        x1, y1 = landmarks[4]  # Thumb tip
        x2, y2 = landmarks[8]  # Index tip
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        dist = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

        # 🔄 Update hover (with glow/sound in Menu class)
        menu.update_hover(cx, cy)

        # ✅ Detect press-and-hold gesture
        if dist < 40:
            selection = menu.update_selection_timer(cx, cy)
            if selection:
                print(f"✅ Selected: {selection}")
                play_sound("assets/sounds/welcome.mp3")

                # 🚀 Launch the selected module
                if selection == "Shapes & Colors":
                    run_shapes_colors(cap, tracker)
                elif selection == "Numbers":
                    run_numbers(cap, tracker)  # ➕ Submenu with math modes
                elif selection == "Counting":
                    run_counting(cap, tracker)
                elif selection == "Spellings":
                    run_spellings(cap, tracker)
                elif selection == "Drawing":
                    run_drawing(cap, tracker)
                elif selection == "Quit":
                    break

                time.sleep(1)  # ⏸ Prevent accidental re-entry

    # ✋ Draw Hand Skeleton
    tracker.draw_hand(frame)

    # 👀 Show App Window
    cv2.imshow("🟦 Touchless Tutor", frame)

    # 🔚 Exit Key
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# 🔒 Cleanup
cap.release()
cv2.destroyAllWindows()

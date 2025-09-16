import cv2
def run_shapes_colors():
    cap = cv2.VideoCapture(0)
    while True:
        _, frame = cap.read()
        frame = cv2.flip(frame, 1)
        cv2.putText(frame, "Lesson: Shapes & Colors", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2)
        cv2.imshow("Shapes & Colors", frame)
        if cv2.waitKey(1) & 0xFF == ord("b"):  # Press 'b' to go back
            break
    cap.release()
    cv2.destroyAllWindows()

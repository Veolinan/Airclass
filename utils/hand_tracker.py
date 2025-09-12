# File: utils/hand_tracker.py
import cv2
import mediapipe as mp
import numpy as np
import time
import math

class HandTracker:
    """
    Tracker using Mediapipe Hands.

    process(frame_bgr) -> returns dict:
      {
        'frame': frame_bgr (may be unchanged),
        'landmarks': list of landmark lists or None,
        'index_pos': (x_px,y_px) or None,
        'thumb_pos': (x_px,y_px) or None,
        'pinch': bool,
        'pinch_start_time': timestamp or None,
        'open_hand': bool
      }
    draw_hand(frame, ...) draws landmarks onto the provided BGR frame.
    """

    def __init__(self, max_num_hands=1, detection_confidence=0.6, tracking_confidence=0.6):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(static_image_mode=False,
                                         max_num_hands=max_num_hands,
                                         min_detection_confidence=detection_confidence,
                                         min_tracking_confidence=tracking_confidence)
        # pinch hysteresis
        self._pinch_state = False
        self._pinch_start_time = None
        self.PINCH_DIST_THRESHOLD = 0.06  # normalized distance
        self.last_results = None
        self.last_landmarks = None

    def process(self, frame):
        if frame is None:
            return {'frame': None, 'landmarks': None,
                    'index_pos': None, 'thumb_pos': None,
                    'pinch': False, 'pinch_start_time': None, 'open_hand': False}

        h, w = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)
        self.last_results = results

        out = {'frame': frame, 'landmarks': None,
               'index_pos': None, 'thumb_pos': None,
               'pinch': False, 'pinch_start_time': None, 'open_hand': False}

        if not results.multi_hand_landmarks:
            self.last_landmarks = None
            self._pinch_state = False
            self._pinch_start_time = None
            return out

        hand = results.multi_hand_landmarks[0]
        lm_px = []
        for lm in hand.landmark:
            lm_px.append((int(lm.x * w), int(lm.y * h), lm.x, lm.y))
        self.last_landmarks = lm_px
        out['landmarks'] = lm_px

        # index tip id 8, thumb tip id 4
        idx = lm_px[8]
        th = lm_px[4]
        out['index_pos'] = (idx[0], idx[1])
        out['thumb_pos'] = (th[0], th[1])

        dx = idx[2] - th[2]
        dy = idx[3] - th[3]
        dist_norm = math.hypot(dx, dy)

        pinch_now = dist_norm < self.PINCH_DIST_THRESHOLD
        if self._pinch_state and dist_norm > self.PINCH_DIST_THRESHOLD * 1.6:
            self._pinch_state = False
            self._pinch_start_time = None
        elif not self._pinch_state and pinch_now:
            self._pinch_state = True
            self._pinch_start_time = time.time()

        out['pinch'] = self._pinch_state
        out['pinch_start_time'] = self._pinch_start_time

        # open hand heuristic: average tip-wrist distance
        wrist = lm_px[0]
        tips = [lm_px[i] for i in (4, 8, 12, 16, 20)]
        avg_dist = np.mean([math.hypot(t[2]-wrist[2], t[3]-wrist[3]) for t in tips])
        out['open_hand'] = avg_dist > 0.22

        return out

    def draw_hand(self, frame, landmark_color=(0,255,0), connections_color=(0,200,0), thickness=2):
        """Draw landmarks (skeleton) on top of provided BGR frame."""
        if frame is None:
            return
        if self.last_results and self.last_results.multi_hand_landmarks:
            for handLms in self.last_results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    handLms,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=landmark_color, thickness=2, circle_radius=6),
                    self.mp_drawing.DrawingSpec(color=connections_color, thickness=2, circle_radius=2)
                )

    def close(self):
        self.hands.close()

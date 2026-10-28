# ═══════════════════════════════════════════════════════════════
#  VIRTUAL HAND MOUSE  —  Complete & Fully Functional
#  Gestures:
#    Index finger move        → Move cursor
#    Pinch (thumb+index)      → Single click  (on release)
#    Pinch twice fast         → Double click
#    All 4 fingers up + move  → Scroll up / down
#    Fist (all fingers folded)→ Screenshot
# ═══════════════════════════════════════════════════════════════

import cv2
import mediapipe as mp
import pyautogui
import time
import math
import numpy as np

# ── PyAutoGUI — remove all built-in delays ──────────────────────
pyautogui.PAUSE    = 0
pyautogui.FAILSAFE = False

# ── MediaPipe ───────────────────────────────────────────────────
mp_hands   = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode        = False,
    max_num_hands            = 1,
    model_complexity         = 0,          # lightest + fastest model
    min_detection_confidence = 0.75,
    min_tracking_confidence  = 0.65,
)

# ── Camera ──────────────────────────────────────────────────────
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS,          30)
cap.set(cv2.CAP_PROP_BUFFERSIZE,   1)      # drop stale frames immediately

if not cap.isOpened():
    print("ERROR: Cannot open camera.")
    exit()

SCREEN_W, SCREEN_H = pyautogui.size()

# ── Cursor smoothing ─────────────────────────────────────────────
ALPHA      = 0.45                          # higher = more responsive, lower = smoother
cur_x      = float(SCREEN_W  // 2)
cur_y      = float(SCREEN_H // 2)

# ── Thresholds ───────────────────────────────────────────────────
PINCH_IN          = 0.052    # distance to register a pinch (tune ±0.005 if needed)
PINCH_OUT         = 0.075    # must open past this to release pinch
DOUBLE_CLICK_GAP  = 0.38     # max seconds between two pinches = double click
SCROLL_SPEED      = 6        # scroll units per frame
SCROLL_UP_ZONE    = 0.33     # index.y < this → scroll up
SCROLL_DOWN_ZONE  = 0.67     # index.y > this → scroll down
SCREENSHOT_DELAY  = 2.5      # seconds between screenshots

# ── State ────────────────────────────────────────────────────────
pinch_active         = False
last_pinch_release   = 0.0   # time of most recent pinch release
pending_single_click = False # True = first pinch done, waiting to see if second comes
last_screenshot_time = 0.0
FONT = cv2.FONT_HERSHEY_SIMPLEX


# ════════════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════════════

def pinch_dist(lm):
    """Euclidean distance thumb tip (4) ↔ index tip (8), normalized."""
    t, i = lm.landmark[4], lm.landmark[8]
    return math.hypot(t.x - i.x, t.y - i.y)


def fingers_up(lm):
    """Returns [index, middle, ring, pinky] as bools — True = finger raised."""
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]   # PIP joints (more stable than tip-2)
    return [lm.landmark[t].y < lm.landmark[p].y for t, p in zip(tips, pips)]


def is_three_finger_pinch(lm):
    """Thumb tip close to both index and middle tip = screenshot gesture."""
    t  = lm.landmark[4]
    i  = lm.landmark[8]
    m  = lm.landmark[12]
    d1 = math.hypot(t.x - i.x, t.y - i.y)
    d2 = math.hypot(t.x - m.x, t.y - m.y)
    return d1 < 0.06 and d2 < 0.06


def label(frame, text, color, row=1):
    y = 40 * row
    cv2.putText(frame, text, (10, y), FONT, 0.9, color, 2, cv2.LINE_AA)


# ════════════════════════════════════════════════════════════════
#  MAIN LOOP
# ════════════════════════════════════════════════════════════════

print("Virtual Hand Mouse running.  Press Q to quit.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (640, 480))

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        result = hands.process(rgb)
        rgb.flags.writeable = True

        now = time.time()

        # ── pending single-click timeout check (outside hand block) ──
        if pending_single_click and (now - last_pinch_release) > DOUBLE_CLICK_GAP:
            pyautogui.click()
            pending_single_click = False

        if result.multi_hand_landmarks:
            lm = result.multi_hand_landmarks[0]

            # draw skeleton
            mp_drawing.draw_landmarks(
                frame, lm, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec((0, 230, 100), 2, 3),
                mp_drawing.DrawingSpec((255, 255, 255), 1),
            )

            f_up   = fingers_up(lm)
            f_count = sum(f_up)
            pd     = pinch_dist(lm)

            # ── PRIORITY 1: 3-FINGER PINCH → screenshot ─────────
            if is_three_finger_pinch(lm):
                if now - last_screenshot_time > SCREENSHOT_DELAY:
                    fname = f"screenshot_{int(now)}.png"
                    pyautogui.screenshot(fname)
                    last_screenshot_time = now
                    print(f"Screenshot saved: {fname}")
                label(frame, "SCREENSHOT", (255, 0, 255))
                cv2.imshow("Virtual Hand Mouse", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue    # skip everything else this frame

            # ── PRIORITY 2: SCROLL — all 4 fingers up ───────────
            if f_count == 4:
                iy = lm.landmark[8].y
                if iy < SCROLL_UP_ZONE:
                    pyautogui.scroll(SCROLL_SPEED)
                    label(frame, "SCROLL UP", (0, 255, 80))
                elif iy > SCROLL_DOWN_ZONE:
                    pyautogui.scroll(-SCROLL_SPEED)
                    label(frame, "SCROLL DOWN", (0, 80, 255))
                else:
                    label(frame, "SCROLL READY", (180, 180, 180))
                cv2.imshow("Virtual Hand Mouse", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                continue    # cursor doesn't move in scroll mode

            # ── PRIORITY 3: PINCH → click logic ─────────────────
            if pd < PINCH_IN:
                if not pinch_active:
                    pinch_active = True   # pinch just started — record entry
                label(frame, "PINCHING...", (255, 220, 0))
 
            elif pd > PINCH_OUT and pinch_active:
                # ── pinch just RELEASED ──
                pinch_active = False
 
                if pending_single_click and (now - last_pinch_release) < DOUBLE_CLICK_GAP:
                    # second pinch release within gap → DOUBLE CLICK
                    pyautogui.doubleClick()
                    pending_single_click = False
                    label(frame, "DOUBLE CLICK", (0, 255, 255))
                    print("Double click")
                else:
                    # first pinch release → arm pending single click
                    pending_single_click = True
 
                last_pinch_release = now
                
            # ── PRIORITY 4: CURSOR MOVE ──────────────────────────
            # Only move when not pinching (pd > PINCH_OUT guard avoids jitter)
            if not pinch_active:
                ix = lm.landmark[8].x
                iy = lm.landmark[8].y

                target_x = max(5, min(SCREEN_W - 5, ix * SCREEN_W))
                target_y = max(5, min(SCREEN_H - 5, iy * SCREEN_H))

                # exponential smoothing
                cur_x += ALPHA * (target_x - cur_x)
                cur_y += ALPHA * (target_y - cur_y)

                pyautogui.moveTo(int(cur_x), int(cur_y), duration=0)

                if pending_single_click:
                    label(frame, "CLICK ARMED", (255, 180, 0))
                else:
                    label(frame, "MOVING", (200, 200, 200))

        else:
            label(frame, "No Hand", (80, 80, 80))

        # pinch % indicator
        cv2.putText(frame, "Q = quit", (500, 470), FONT, 0.5, (100,100,100), 1, cv2.LINE_AA)
        cv2.imshow("Virtual Hand Mouse", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    cap.release()
    hands.close()
    cv2.destroyAllWindows()
    print("Closed cleanly.")
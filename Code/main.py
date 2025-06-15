import cv2
import time
import mediapipe as mp  # MediaPipe for hand tracking
import pyautogui as pag
import win32api
import win32con
media_state_is_playing = None


def media_pause():
    global media_state_is_playing
    if media_state_is_playing is not True:
        try:
            win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
            win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0)
            media_state_is_playing = True
        except Exception:
            pass


def media_play():
    global media_state_is_playing
    if media_state_is_playing is not False:
        try:
            win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, 0, 0)
            win32api.keybd_event(win32con.VK_MEDIA_PLAY_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0)
            media_state_is_playing = False
        except Exception:
            pass


def media_seek(direction):
    try:
        if direction == "forward":
            pag.press('right')
        elif direction == "backward":
            pag.press('left')
    except Exception as e:
        print(f"Could not simulate key press: {e}")


def detect_gesture(fingers, lmlist):
    if not lmlist:
        return "none"
    if fingers == [1, 1, 0, 0, 0]:
        return "volume"
    elif fingers == [0, 0, 0, 0, 0]:
        return "pause"
    elif fingers == [1, 1, 1, 1, 1]:
        return "play"
    elif fingers == [0, 1, 1, 0, 0]:
        return "seek_forward"
    elif fingers == [0, 1, 1, 1, 0]:
        return "seek_backward"
    elif fingers == [0, 1, 1, 1, 1]:
        return "mute"

    return "none"
print("GESTURE MEDIA CONTROLLER FOR WINDOWS")
print("Pinch (thumb + index): Volume control")
print("Closed fist: Pause media")
print("Open palm: Play media")
print("Peace sign: Seek forward (10s)")
print("Three fingers: Seek backward (10s)")
print("\nPress 'q' in the camera window to quit.")

wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

last_gesture = "none"
gesture_time = 0
gesture_cooldown = 1.0
current_action = "None"
volBar, volPer = 400, 0
minVol, maxVol = 0, 100

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    image = cv2.flip(image, 1)

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    lmList = []
    if results.multi_hand_landmarks:
        myHand = results.multi_hand_landmarks[0]
        mp_drawing.draw_landmarks(
            image, myHand, mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style()
        )
        for id, lm in enumerate(myHand.landmark):
            h, w, c = image.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            lmList.append([id, cx, cy])

    if lmList:
        fingers = []
        tipIds = [4, 8, 12, 16, 20]

        if lmList[tipIds[0]][1] < lmList[tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        current_gesture = detect_gesture(fingers, lmList)

        if current_gesture != "none" and current_gesture != last_gesture:
            if time.time() - gesture_time > gesture_cooldown:
                if current_gesture == "play":
                    media_play()
                    current_action = "Play"
                elif current_gesture == "pause":
                    media_pause()
                    current_action = "Pause"
                elif current_gesture == "seek_forward":
                    media_seek("forward")
                    current_action = "Seek Forward"
                elif current_gesture == "seek_backward":
                    media_seek("backward")
                    current_action = "Seek Backward"
                elif current_gesture == "mute":
                    pag.press("volumemute")
                    current_action = "Mute"
                last_gesture = current_gesture
                gesture_time = time.time()
        if current_gesture == "volume":
            current_action = "Volume Control"
            x1, y1 = lmList[4][1], lmList[4][2]  # Thumb tip
            x2, y2 = lmList[8][1], lmList[8][2]  # Index‑finger tip
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            cv2.circle(image, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(image, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
            # draw the line connecting thumb & finger
            cv2.line(image, (x1, y1), (x2, y2), (255, 0, 255), 3)

            # compute distance without floor‑division and cast to int
            length = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)

            # map length to a reasonable volume-up/down threshold
            if length > 65:
                pag.press("volumeup")
            else:
                pag.press("volumedown")

    cv2.putText(image, f'Action: {current_action}', (10, 40), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    cv2.imshow('Gesture Media Controller', image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
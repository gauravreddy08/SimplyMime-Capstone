import mediapipe as mp
import cv2 as cv
import math
import pyautogui
import osascript

w, h = pyautogui.size()
mp_hands = mp.solutions.hands

pyautogui.FAILSAFE = False
volume = 40

hands = mp_hands.Hands(
    static_image_mode=False,
    min_detection_confidence=0.7)

def get_data(results):
    if results.multi_hand_landmarks == None:
        return "", "No Hands"
    hall_marks = results.multi_hand_landmarks[0]
    for idx, hand_handedness in enumerate(results.multi_handedness):
        side = hand_handedness.classification[0].label
    res = []
    # THUMB
    if side=="Right":
        res.append(1 if hall_marks.landmark[mp_hands.HandLandmark.THUMB_TIP].x < hall_marks.landmark[mp_hands.HandLandmark.THUMB_MCP].x else 0)
    else:
        res.append(0 if hall_marks.landmark[mp_hands.HandLandmark.THUMB_TIP].x < hall_marks.landmark[mp_hands.HandLandmark.THUMB_MCP].x else 1)
        
    
    # INDEX
    res.append(1 if hall_marks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y < hall_marks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].y else 0)
    
    # MIDDLE
    res.append(1 if hall_marks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP].y < hall_marks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y else 0)
    
    # RING
    res.append(1 if hall_marks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP].y < hall_marks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].y else 0)
    
    # PINKY
    res.append(1 if hall_marks.landmark[mp_hands.HandLandmark.PINKY_TIP].y < hall_marks.landmark[mp_hands.HandLandmark.PINKY_MCP].y else 0)

    return side, res

print("CAM")
text=""
max = False
min = False

cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
i = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    results = hands.process(cv.flip(cv.cvtColor(frame, cv.COLOR_BGR2RGB), 1))
    side, data = get_data(results)

    if data == [1,1,0,0,0]:
        hall_marks = results.multi_hand_landmarks[0]
        x1, y1 = hall_marks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x , hall_marks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
        x2, y2 = hall_marks.landmark[mp_hands.HandLandmark.THUMB_TIP].x , hall_marks.landmark[mp_hands.HandLandmark.THUMB_TIP].y
        [x, y] = (x1+x2)*w/2, (y1+y2)*h/2
        pyautogui.moveTo(x,y)

        if math.dist([x1,y1], [x2,y2])<0.05 and i>=4:
            print("clicked")
            pyautogui.click(x,y)
            i=0
    if data == [0,1,1,0,0]:
        if side=="Right":
            pyautogui.press("up", presses=8)
        else:
            pyautogui.press("down", presses=8)
    elif data == [0,1,1,1,0]:
        if side=="Right":
            volume = 100 if volume>=100 else volume+10
        else:
            volume = 0 if volume<=0 else volume-10
        osascript.osascript(f"set volume output volume {volume}")
    i+=1
        
     
    cv.putText(frame, 
                str(data), 
                (50, 50), 
                cv.FONT_HERSHEY_SIMPLEX, 1, 
                (0, 255, 255), 
                2, 
                cv.LINE_4)

    cv.imshow('frame', frame)

    if cv.waitKey(1) == ord('q'):
        break


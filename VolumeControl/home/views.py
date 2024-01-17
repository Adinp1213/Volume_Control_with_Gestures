from django.shortcuts import render,HttpResponse,redirect
import cv2
import mediapipe as mp
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np
import threading
# Create your views here.
def index(request):
       return render(request,'index.html')

def about_us(request):
       return render(request,'about_us.html')

def volume_control(request):
    try:
        threading.Thread(target=run_volume_control_script).start()
        #return HttpResponse("Volume control script is running. Check the console for feedback. Press SPACEBAR to exit the console")
        return render(request,'running.html')
    except Exception as e:
        return HttpResponse(f"Error: {e}")

def run_volume_control_script():
    cap = cv2.VideoCapture(0)  # Checks for the camera
    mpHands = mp.solutions.hands  # Detects hand/finger
    hands = mpHands.Hands()  # Complete the initialization configuration of hands
    mpDraw = mp.solutions.drawing_utils

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volbar = 400

    finger_tip_ids = [4, 8, 12, 16, 20]  # Tip IDs excluding thumb (0-indexed)
    fist_threshold = 0.85  # Adjust this value based on the desired sensitivity for detecting a fist

    while True:
        success, img = cap.read()  # If the camera works, capture an image
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert to RGB

        # Collection of gesture information
        results = hands.process(imgRGB)  # Complete the image processing.

        lmList = []  # Empty list
        if results.multi_hand_landmarks:  # List of all hands detected.
            for handLandmark in results.multi_hand_landmarks:
                for id, lm in enumerate(handLandmark.landmark):  # Adding counter and returning it
                    h, w, _ = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])  # Adding to the empty list 'lmList'
                mpDraw.draw_landmarks(img, handLandmark, mpHands.HAND_CONNECTIONS)

            num_fingers = 0  # Initialize the finger count

            if lmList:
                # Calculate the average y-coordinate of the finger tips
                avg_y_coordinate = np.mean([lmList[i][2] for i in finger_tip_ids])

                # Check if the hand is in a fist position
                is_fist = all(lmList[finger_id][2] > lmList[4][2] for finger_id in finger_tip_ids[1:])

                if is_fist:
                    num_fingers = 0  # Fist detected
                else:
                    # Count extended fingers based on finger tip positions, excluding the thumb
                    num_fingers = sum(1 for finger_id in finger_tip_ids if lmList[finger_id][2] < lmList[finger_id - 2][2])

            # Adjust the volume based on the number of fingers
            target_vol = np.interp(num_fingers, [1, 5], [0.0, 1.0])  # Adjusted range for volume levels
            volbar = np.interp(num_fingers, [1, 5], [400, 150])

            # Set the volume directly based on the percentage
            volume.SetMasterVolumeLevelScalar(target_vol, None)

            # Draw the volume bar and percentage on the screen
            cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 255), 4)  # Initial position, ending position, RGB, thickness
            cv2.rectangle(img, (50, int(volbar)), (85, 400), (0, 0, 255), cv2.FILLED)
            cv2.putText(img, f"{int(target_vol * 100)}%", (10, 70), cv2.FONT_ITALIC, 1, (0, 255, 98), 3)
            #cv2.putText(img, f"{int(num_fingers)}fingers", (10, 35), cv2.FONT_ITALIC, 1, (0, 255, 98), 3)

        cv2.imshow('Image', img)  # Show the video
        if cv2.waitKey(1) & 0xff == ord(' '):  # By using spacebar, delay will stop
            break

    cap.release()  # Stop the camera
    cv2.destroyAllWindows() 
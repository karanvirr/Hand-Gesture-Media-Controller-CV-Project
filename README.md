"# Hand-Gesture-Media-Controller-CV-Project" 
Gesture Media Controller uses computer vision through OpenCV and MediaPipe to detect hand gestures and translate them into media control actions like play, pause, mute, seek and volume level control.

To run this project, you must have Python installed on your device.

# Steps to run:

1) Install the required dependencies by running the following command on the terminal:
	pip install opencv-python mediapipe pyautogui pywin32

	OR

	pip install -r requirements.txt

2) After installing dependencies, run the main Python script with the following command:
	python main.py

3) A small window will appear with a live video feed from the webcam.

4) Open YouTube and play a video.

5) Make the gestures (fist, 5 fingers open, peace sign, etc) in front of the webcam.

6) The corresponding media control action will be performed and will be shown in the webcam feed.

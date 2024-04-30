import numpy as np
import cv2
import sys


video_path = sys.argv[1]
video = cv2.VideoCapture(video_path)
success, frame = video.read()
i = 0
while success:
    frame = cv2.resize(frame, (176, 144))
    if i==15953:
        cv2.imwrite("frame15953.jpg", frame)
        break
    i += 1
    success, frame = video.read()
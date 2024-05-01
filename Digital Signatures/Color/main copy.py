import numpy as np
import cv2
from sklearn.cluster import KMeans
import sys
import time
import json
from collections import Counter

video_path = sys.argv[1]
video = cv2.VideoCapture(video_path)
success, frame = video.read()
colors = {}
i = 0
start = time.time()
data = {}
while success:

    frame = cv2.resize(frame, (176, 144))
    """
    blue = cv2.calcHist([frame], [0], None, [256], [0, 256])
    green = cv2.calcHist([frame], [1], None, [256], [0, 256])
    red = cv2.calcHist([frame], [2], None, [256], [0, 256])
    colors[i] = frame
    """

    # """
    frame = frame.reshape((-1,3))
    pixels = [tuple(i) for i in frame]

    color = Counter(pixels)
    color = color.most_common(10)
    color = [list(i[0]) for i in color]
    color = [list(map(int, i)) for i in color]
    data[i] = color
    # """

    i += 1
    success, frame = video.read()

print("Time taken:", time.time() - start)

with open("data.json", "w") as file:
    json.dump(data, file)

video.release()
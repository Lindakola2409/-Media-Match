import numpy as np
import cv2
from sklearn.cluster import KMeans
import sys
import time
import json

video_path = sys.argv[1]
video = cv2.VideoCapture(video_path)
success, frame = video.read()
colors = {}
i = 0
start = time.time()
while success:
    # Try manually finding the distribution of colors in the frame (iterating through each pixel)
    frame = cv2.resize(frame, (176, 144))

    frame = frame.reshape((-1,3))
    frame = np.float32(frame)
    kmeans = KMeans(n_clusters=3).fit(frame)

    frame = kmeans.cluster_centers_
    frame = frame.astype(int)

    colors[i] = frame.tolist()
    i += 1
    success, frame = video.read()

print("Time taken:", time.time() - start)

with open("data.json", "w") as file:
    json.dump(colors, file)

video.release()
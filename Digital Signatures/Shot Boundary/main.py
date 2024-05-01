from findframe import *
import cv2
import numpy as np
import sys
import json


def shotBoundary(videopath):
    cap = cv2.VideoCapture(str(videopath))
    curr_frame = None
    prev_frame = None
    frame_diffs = []
    frames = []
    success, frame = cap.read()
    i = 0
    FRAME = Frame(0, 0)
    while (success):
        luv = cv2.cvtColor(frame, cv2.COLOR_BGR2LUV)
        curr_frame = luv
        """
        
        calculate the difference between frames 
        
        """

        # try to calculate max difference between next 30 frames
        if curr_frame is not None and prev_frame is not None:
            diff = cv2.absdiff(curr_frame, prev_frame)
            diff_sum = np.sum(diff)
            diff_sum_mean = diff_sum / (diff.shape[0] * diff.shape[1])
            frame_diffs.append(diff_sum_mean)
            frame = Frame(i, diff_sum_mean)
            frames.append(frame)
        elif curr_frame is not None and prev_frame is None:
            diff_sum_mean = 0
            frame_diffs.append(diff_sum_mean)
            frame = Frame(i, diff_sum_mean)
            frames.append(frame)

        prev_frame = curr_frame
        i = i + 1
        success, frame = cap.read()
    cap.release()

    #detect the possible frame
    frame_return, start_id_spot_old, end_id_spot_old = FRAME.find_possible_frame(frames)

    #optimize the possible frame
    new_frame, start_id_spot, end_id_spot = FRAME.optimize_frame(frame_return, frames)

    #store the result
    start = np.array(start_id_spot)[np.newaxis, :]
    end = np.array(end_id_spot)[np.newaxis, :]
    spot = np.array([])
    if len(end_id_spot) > 0:
        spot = np.concatenate((start.T, end.T), axis=1)
    return spot

def generate():
    data = {}
    for i in range(1,21):
        videopath = "./Video Dataset/video" + str(i) + ".mp4"
        spot = shotBoundary(videopath)
        data[i] = spot.tolist()
    with open("./Digital Signatures/Shot Boundary/database.json", "w") as file:
        json.dump(data, file)

def difference(arr):
    arr = [i[1]-i[0] for i in arr]
    arr = arr[1:-1]
    return arr

if __name__ == "__main__":
    
    # generate()
    
    videopath = sys.argv[1]
    spot = shotBoundary(videopath)
    data = {}
    data[0] = spot.tolist()
    with open("./Digital Signatures/Shot Boundary/data.json", "w") as file:
        json.dump(data, file)

    if len(data[0]) > 2: # At least 2 shot boundaries
        with open("./Digital Signatures/Shot Boundary/database.json", "r") as file:
            database = json.load(file)

        query_shot = difference(data[0])
        
        for key in database:
            video_shot = difference(database[key])
            if len(video_shot) < 2:
                continue
            # Compare the query shot with the video shot as a subarray
            for i in range(len(video_shot) - len(query_shot) + 1):
                if video_shot[i:i+len(query_shot)] == query_shot:
                    frameno = database[key][i+1][0] - data[0][1][0] - 1 
                    print("Start at frame", frameno, "in video", key)
    else:
        print("No shot boundaries detected.")        
            
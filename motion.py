import math
import sys
from flask import Flask, render_template, request, jsonify
import csv
import time
import cv2 as cv
import numpy as np
import pandas as pd
import webbrowser
from shotboundary import *
from sound import *
import re
app = Flask(__name__)

# Paths
CSVFileName = 'New.csv'
FRAMERATE = 30.0


def createSignatures(videoPath):
    print("Getting the motion sig of QueryVideo " + videoPath)
    start_time = time.time()
    # The video feed is read in as a VideoCapture object
    cap = cv.VideoCapture(videoPath)

    # Initialize variables to store motion signatures
    frame_index = 0
    motion_signatures = []

    # isMoreFrames = a boolean return value from getting the frame
    # first_frame = the first frame in the entire video sequence
    isMoreFrames, first_frame = cap.read()

    # Converts frame to grayscale because we only need the luminance channel for detecting edges - less computationally expensive
    prev_gray = cv.cvtColor(first_frame, cv.COLOR_BGR2GRAY)
    # Get the frame rate of the video
    frame_rate = cap.get(cv.CAP_PROP_FPS)

    # Process each frame in the video
    while (cap.isOpened()):

        # isMoreFrames = a boolean return value from getting the frame,
        # frame = the current frame being projected in the video
        isMoreFrames, currFrame = cap.read()

        # Break the loop if there are no more frames
        if not isMoreFrames:
            break

        # Converts each frame to grayscale
        gray = cv.cvtColor(currFrame, cv.COLOR_BGR2GRAY)

        # Calculates dense optical flow by Farneback method
        flow = cv.calcOpticalFlowFarneback(prev_gray, gray,
                                           None,
                                           0.5, 3, 15, 3, 5, 1.2, 0)

        # Computes the magnitude of the 2D vectors
        magnitude = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)

        # Compute the average magnitude as the motion statistic for the frame
        motion_statistic = np.mean(magnitude)

        # Store the frame index and motion statistic
        motion_signatures.append((frame_index, motion_statistic))
        # Updates previous frame
        prev_gray = gray
        frame_index += 1

        # Frames are read by intervals of 1 millisecond. The
        # programs breaks out of the while loop when the
        # user presses the 'q' key
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    # The following frees up resources and
    # closes all windows
    cap.release()
    cv.destroyAllWindows()
    PrintElapsedTime(start_time)
    return motion_signatures, frame_rate


# Threshold is the percentage of match before a to confirm simlarity
def find_starting_frame(query_signature, video_signatures, window_size=100, threshold=0.8):
    query_len = len(query_signature)
    query_motion_stats = [entry[1] for entry in query_signature]

    best_match_index = None
    max_similarity = -1

    for i in range(len(video_signatures) - query_len + 1):
        window = video_signatures[i:i + query_len]
        window_motion_stats = [entry[1] for entry in window]
        similarity = np.corrcoef(query_motion_stats, window_motion_stats)[0, 1]
        if similarity > max_similarity:
            max_similarity = similarity
            best_match_index = i

    if max_similarity > threshold:
        return best_match_index, max_similarity, True
    else:
        return best_match_index, max_similarity, False


def PrintElapsedTime(start_time):
    end_time = time.time()
    elapsed_time = end_time - start_time
    elapsed_time = round(elapsed_time, 5)
    print(f"** Completed Task {elapsed_time} seconds ** \n")


def calculate_timestamp(frame_index, frame_rate):
    # Calculate the timestamp in seconds
    timestamp = frame_index / frame_rate
    return timestamp

def PreProcess(fileName):
    print("Preprocessing")
    database_motion_signatures = {}
    start_time = time.time()
    database_motion_signatures = {}
    with open(fileName, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            video_path, frame_index, motion_statistic = row
            frame_index = int(frame_index)
            motion_statistic = float(motion_statistic)
            if video_path not in database_motion_signatures:
                database_motion_signatures[video_path] = []
            database_motion_signatures[video_path].append((frame_index, motion_statistic))
    PrintElapsedTime(start_time)
    return database_motion_signatures

def motion(query_motion_signature, database_motion_signatures):
    matches = {}
    for videoPath, currVidSig in database_motion_signatures.items():
        frame, percent, bIsMatched = find_starting_frame(query_motion_signature, database_motion_signatures[videoPath])
        percent = round((percent * 100), 1)
        matches[videoPath] = {"percentage": percent, "frame": frame}
        #Printing
        if bIsMatched:
            tempFrame = (frame - 1)
            timestamp = tempFrame / FRAMERATE / 60
            second, min = math.modf(timestamp)
            second = second * 60
            secondStr = str(int(second))
            timestampStr = str(int(min)) + ":" + str(int(second))
            if len(secondStr) == 1:
                if(secondStr == "0"):
                    timestampStr = timestampStr + "0"
                else:
                    timestampStr = "0" + timestampStr
            print(f"--->{videoPath} [MATCH] Similarity: {percent}% At Frame {frame} At time {timestampStr}")
        else:
            print(f"\t{videoPath} [No Match] Similarity: {percent}%")
    return matches

def motion_best(motion_score):

    # check top 3 scores and if they are within 5% score range of each other
    motion_score = {re.search('static/video(.+?).mp4',k).group(1):v for k,v in motion_score.items()}
    motion_score = sorted(motion_score.items(), key=lambda x: x[1]['percentage'], reverse=True)
    highest_score = motion_score[0][1]['percentage']
    top_scores = list(filter(lambda x: (highest_score - x[1]['percentage'] < 5),motion_score[:3]))
    if top_scores[0][1]['percentage'] == 99.9:
        return {top_scores[0][0]:top_scores[0][1]}
    top_scores = {i[0]:i[1] for i in top_scores}
    return top_scores

@app.route('/')
def index():
    veryFirstStartTime =  time.time()
    queryVideoName = ""
    queryAudio = ""
    if len(sys.argv) == 3:
        queryVideoName = sys.argv[1]
        queryAudio = sys.argv[2]
    else:
        return render_template('index.html',
                           query_video_path="video1.mp4",
                           original_video_path="video3_1_modified.mp4",
                           matching_frame=0, 
                           percent=0,
                           videoPath=0,
                            time_stamp = 0,
                           timestampStr="00:00")

    queryVideoPath = "static/Videos/Query Videos/" + queryVideoName
    queryAudioPath = "static/Videos/Query Videos/" + queryAudio
    # run shot boundary detection
    shots = shotDetect(queryVideoPath)
    shot_video_list = {"static/video"+i+".mp4" for i in list(shots.keys())}
    print("Shots:",shots)

    query_motion_signature, FRAMERATE = createSignatures(queryVideoPath)
    database_motion_signatures = PreProcess(CSVFileName)

    filtered_database_motion_signatures = {x: database_motion_signatures[x] for x in shot_video_list}

    motion_scores = {}
    bestMatchPath = ""
    bestFrame = -1
    bestPercent = 0

    # Check if there is a motion match with shot boundary filtered videos
    if len(shot_video_list) > 0:
        motion_scores = motion(query_motion_signature, filtered_database_motion_signatures)
        for i in shots.keys():
            path = "static/video"+i+".mp4"
            if motion_scores[path]['frame']-1 in shots[i] and motion_scores[path]['percentage'] > 85 and motion_scores[path]['percentage'] > bestPercent:
                bestMatchPath = path
                bestFrame = motion_scores[bestMatchPath]['frame']
                bestPercent = motion_scores[bestMatchPath]['percentage']
    
    if bestFrame == -1:
        # if no exact match found, calculate motion on remaining videos
        remaining_videos = {"static/video"+str(i)+".mp4" for i in range(1,21) } - shot_video_list
        filtered_database_motion_signatures = {x: database_motion_signatures[x] for x in remaining_videos}
        remaining_scores = motion(query_motion_signature, filtered_database_motion_signatures)
        motion_scores.update(remaining_scores)

        top_scores = motion_best(motion_scores)
        print("Top scores:",top_scores)
        if len(top_scores) == 1: # only one video is within 5% score range
            bestMatchPath = "static/video"+list(top_scores.keys())[0]+".mp4"
            bestFrame = motion_scores[bestMatchPath]['frame']
            bestPercent = motion_scores[bestMatchPath]['percentage']
        else:

            # if more than one video is within 5% score range, run audio signature
            audio_score = audio(queryAudioPath, list(top_scores.keys()))
            print("Audio Scores:",audio_score)

            # Compare weighted sum of squares
            bestScore = 0  
            for i in audio_score.keys():
                scoreAudio =  (round((1-audio_score[i][1])*100,1))**2
                scoreMotion = top_scores[i]['percentage']**2*1.21 # 1.21 is the weight for motion score
                score = scoreAudio + scoreMotion
                if score > bestScore:
                    bestScore = score
                    bestMatchPath = "static/video"+i+".mp4"
                    if scoreAudio > scoreMotion: # Trust audio score more
                        bestFrame = audio_score[i][0]+1
                        bestPercent = round((1-audio_score[i][1])*100,1)
                    else: # Trust motion score more
                        bestFrame = motion_scores[bestMatchPath]['frame']
                        bestPercent = motion_scores[bestMatchPath]['percentage']

    # Calculate timestamp
    tempFrame = (bestFrame)
    timestamp = tempFrame / FRAMERATE / 60
    second, minute = math.modf(timestamp)
    second = second * 60
    secondStr = str(int(second))
    timestampStr = str(int(minute)) + ":" + str(int(second))
    if len(secondStr) == 1:
        timestampStr = timestampStr + "0"
    strToRemove = "static/"
    bestMatchPath = "Videos/" + bestMatchPath.replace(strToRemove, "")
    queryVideoPath = queryVideoPath.replace(strToRemove, "")
    # Render the HTML template with the query video path and matching frame details
    print(f"\n{bestMatchPath} [BEST MATCH] Similarity: {bestPercent}% At Frame {tempFrame} At time {timestampStr}")
    PrintElapsedTime(veryFirstStartTime)
    return render_template('index.html',
                           query_video_path=queryVideoPath,
                           original_video_path=bestMatchPath,
                           matching_frame=tempFrame, 
                           percent=bestPercent,
                           videoPath=bestMatchPath,
                            time_stamp = (tempFrame/ FRAMERATE),
                           timestampStr=timestampStr)

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:5000/')
    app.run(debug=False)

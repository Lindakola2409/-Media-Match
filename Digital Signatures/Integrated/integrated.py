from shotboundary import *
from sound import *
# import files for each signatures
import sys
import cv2
import time

# REPLACE with the real function
def motion(signature, query_path, video_list):
    return {'3':[13350,99.6],'4':[8880,99.9],'5':[9305,93.4],'2':[8340,92.5],'6':[12240,99.9]}

def motion_best(motion_score):

    # check top 3 scores and if they are within 5% score range of each other
    motion_score = sorted(motion_score.items(), key=lambda x: x[1][1], reverse=True)
    print("Motion score:",motion_score)

    highest_score = motion_score[0][1][1]
    top_scores = list(filter(lambda x: (highest_score - x[1][1] < 5),motion_score[:3]))
    top_scores = {i[0]:i[1] for i in top_scores}
    print("Top scores:",top_scores)
    return top_scores


def main():
    query_path = sys.argv[1]
    query_video = cv2.VideoCapture(query_path)
    duration = query_video.get(cv2.CAP_PROP_FRAME_COUNT)/30
    query_video.release()
    motion_scores = []

    if duration > 30:
        shots = shotDetect(query_path)
        video_list = {"video"+i+".mp4" for i in list(shots.keys())}
        print("Shots:",shots)
        motion_scores = {}
        # preprocess query motion signature
        query_motion_signature = 0 # REPLACE with real function

        if len(video_list) > 0:
            motion_scores = motion(query_motion_signature,query_path, video_list) # calculate motion for videos detected by shot boundary
            for i in motion_scores.keys():
                if i in shots.keys() and motion_scores[i][0] in shots[i]: # exact match found with motion and shot boundary
                    print("Exact shot + motion match found:",i)
                    return [i,motion_scores[i]]
            
        # if no exact match found, run motion on remaining videos
        remaining_videos = set(range(1,21)) - video_list
        remaining_scores = motion(query_motion_signature,query_path, remaining_videos)
        motion_scores.update(remaining_scores)
        motion_scores = motion_best(motion_scores)
        if len(motion_scores) == 1: # only one video is within 5% score range
            return motion_scores[0]
    
    else: # duration < 30
        # preprocess query motion signature
        query_motion_signature = 0 # REPLACE with real function

        motion_scores = motion(query_motion_signature,query_path, set(range(1,21)))
        motion_scores = motion_best(motion_scores)
        if len(motion_scores) == 1: # only one video is within 5% score range
            return motion_scores[0]
        
        # check with shot boundary
        shots = shotDetect(query_path)
        video_list = {"video"+i+".mp4" for i in list(shots.keys())}
        print("Shots:",shots)

        if len(video_list) > 0:
            for i in motion_scores.keys():
                if i in shots.keys() and motion_scores[i][0] in shots[i]: # exact match found with motion and shot boundary
                    print("Exact shot + motion match found:",i)
                    return [i,motion_scores[i]]

    # if more than one video is within 5% score range, run audio signature
    audio_score = audio(query_path.replace('.mp4', '.wav'), list(motion_scores.keys()))
    print("Audio score:",audio_score)

    # compare weighted sum of squares
    output = None
    return output

if __name__ == "__main__":
    start = time.time()
    output = main()
    print("Output:",output)
    print("Time taken:",time.time()-start)

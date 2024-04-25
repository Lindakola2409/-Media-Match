from findframe import *
import cv2
import numpy as np
import sys


if __name__ == "__main__":
    # dataload
    videopath = sys.argv[1]
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

        # temp = [112	,231	,506	,737	,1259	,1786	,2303	,2408	,2689	,2918	,3650	,3946	,4337	,6188	,7379	,7789	,9400	,10278	,12417	,13080	,13503	,13575	,13724	,13911	,13988	,14175	,14696	,14995	,15150	,15257	,15466	,15660	,15748	,16681	,17664	,17807	,18755	,19169	,19810	,20238	,21914	,22449	,22652	,22879	,23010	,23142	,24066	,24562	,24984]
        # if i in temp or i+1 in temp:
        #     cv2.imshow('frame', frame)
        #     cv2.waitKey(0)

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

    # print("start_id_spot_old", start_id_spot_old)
    # print("end_id_spot_old", end_id_spot_old)

    #optimize the possible frame
    new_frame, start_id_spot, end_id_spot = FRAME.optimize_frame(frame_return, frames)

    #store the result
    start = np.array(start_id_spot)[np.newaxis, :]
    end = np.array(end_id_spot)[np.newaxis, :]
    spot = np.concatenate((start.T, end.T), axis=1)
    np.savetxt('./result.txt', spot, fmt='%d', delimiter='\t')

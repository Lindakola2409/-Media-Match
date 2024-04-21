import cv2
import imutils
import sys
import os

def detect_scene():
    video_path = sys.argv[1]
    output = ".\output"
    max_percent = 90
    min_percent = 80
    captured = False
    # count = 0

    # initialize the background subtractor
    fgbg = cv2.createBackgroundSubtractorMOG2()

    vs = cv2.VideoCapture(str(video_path))
    (W, H) = (None, None)

    while(True):
        # ret: whether the frame is read correctly or not
        ret, frame = vs.read()
        if frame is None:
            break

        orig = frame.copy()
        frame = imutils.resize(frame, width=600) #??
        mask = fgbg.apply(frame)

        curFrameNo = vs.get(cv2.CAP_PROP_POS_FRAMES)
        # remove noise
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        if W is None or H is None:
            (W, H) = mask.shape[:2]

        # black: 0, white/changing part: 1
        p = (cv2.countNonZero(mask)/float(W * H))*100

        # print("Foreground percentage: {} at frame {}".format(p, curFrameNo))

        if p < min_percent and not captured:
            filename = "Boundary{}.png".format(curFrameNo)
            path = os.path.sep.join([output, filename])
            cv2.imwrite(filename, orig)
            captured = True
            print("here1")
            # count += 1
        elif captured and p >= max_percent:
            # return to capturing mode
            print("here")
            captured = False

        # cv2.putText(orig, str(curFrameNo), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        # cv2.imshow('Orig', orig)
        # cv2.imshow('frame', mask)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break
        # time.sleep(0.5)


    # When everything done, release the capture
    vs.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    detect_scene()
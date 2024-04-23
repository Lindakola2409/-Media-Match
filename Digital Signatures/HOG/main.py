import cv2
import sys
import json
import numpy as np
import time
from sklearn.decomposition import PCA

# Function to compute HOG descriptors for a frame
def compute_hog(frame):
    # Initialize HOG descriptor
    hog = cv2.HOGDescriptor()

    # Compute HOG descriptors for the frame
    hog_descriptor = hog.compute(frame)

    return hog_descriptor

# # Function to compare two HOG descriptors
def compare_hog_descriptors(descriptor1, descriptor2):
    # Compute Euclidean distance between the HOG descriptors
    distance = cv2.norm(descriptor1, descriptor2, cv2.NORM_L2)
    return distance

if __name__ == "__main__":
    videopath1, videopath2= sys.argv[1], sys.argv[2]
    cap = cv2.VideoCapture(str(videopath1))
    # Read the first frame
    success, frame = cap.read()
    i = 0
    while(success):
        # compute hog descriptor for the frame
        if(i == 12419):
        # if i == 6750:
            frame = cv2.resize(frame, (176,144))
            hog_descriptor1 = compute_hog(frame)
            hog_descriptors = np.array(hog_descriptor1).reshape(100, -1)
            n_components = 1  # Number of principal components to retain
            pca = PCA(n_components=n_components)
            pca.fit(hog_descriptors)

            # Transform the HOG descriptors using the learned PCA transformation
            hog_descriptors_pca1 = pca.transform(hog_descriptors)
            cv2.imwrite("frame1.png", frame)

            with open('output.txt', 'w') as filehandle:
                json.dump(hog_descriptors_pca1.tolist(), filehandle)
        success, frame = cap.read()
        i += 1
    
    
    # Release video capture
    cap.release()

    cap = cv2.VideoCapture(str(videopath2))

    # Read the first frame
    success, frame = cap.read()
    i = 0
    while(success):
        # compute hog descriptor for the frame
        if(i == 177):
            hog_descriptor2 = compute_hog(frame)
            hog_descriptors = np.array(hog_descriptor2).reshape(100, -1)
            n_components = 1  # Number of principal components to retain
            pca = PCA(n_components=n_components)
            pca.fit(hog_descriptors)
            hog_descriptors_pca2 = pca.transform(hog_descriptors)
            cv2.imwrite("frame2.png", frame)
        success, frame = cap.read()
        i += 1

    cap.release()

    # Compare HOG descriptors of the two frames
    start = time.time()
    distance1 = compare_hog_descriptors(hog_descriptor1, hog_descriptor2)
    end = time.time()
    print("Time taken to compare HOG descriptors of two frames:", end - start)
    start = time.time()
    distance2 = compare_hog_descriptors(hog_descriptors_pca1, hog_descriptors_pca2)
    end = time.time()
    print("Time taken to compare HOG descriptors of two frames after PCA:", end - start)
    print("Distance between the two frames:", distance1)
    print("Distance between the two frames:", distance2)
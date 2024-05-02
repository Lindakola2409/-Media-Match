import json
import timeit
import numpy as np
import librosa
from moviepy.editor import VideoFileClip

database = {
    "./Video Dataset/video1.mp4": None,
    "./Video Dataset/video2.mp4": None,
    "./Video Dataset/video3.mp4": None,
    "./Video Dataset/video4.mp4": None,
    "./Video Dataset/video5.mp4": None,
    "./Video Dataset/video6.mp4": None,
    "./Video Dataset/video7.mp4": None,
    "./Video Dataset/video8.mp4": None,
    "./Video Dataset/video9.mp4": None,
    "./Video Dataset/video10.mp4": None,
    "./Video Dataset/video11.mp4": None,
    "./Video Dataset/video12.mp4": None,
    "./Video Dataset/video13.mp4": None,
    "./Video Dataset/video14.mp4": None,
    "./Video Dataset/video15.mp4": None,
    "./Video Dataset/video16.mp4": None,
    "./Video Dataset/video17.mp4": None,
    "./Video Dataset/video18.mp4": None,
    "./Video Dataset/video19.mp4": None,
    "./Video Dataset/video20.mp4": None,
}


def extract_audio_from_video(video_path):
    """Extracts audio from the video file and returns the path to the temporary audio file."""
    video = VideoFileClip(video_path)
    audio_path = video_path.replace('.mp4', '.wav')
    video.audio.write_audiofile(audio_path)
    return audio_path


def compute_mfcc(audio_path, n_mfcc=13):
    """Computes the MFCCs of the audio file and returns them as a 2D array."""
    y, sr = librosa.load(audio_path, sr=None)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc, hop_length=512, win_length=2048)
    return mfcc  # Return the full MFCC array, not just the mean.


def preprocess_database():
    """Preprocesses each video in the database to compute and store their digital signatures."""
    temp = {}
    for video_path in database.keys():
        audio_path = extract_audio_from_video(video_path)
        mfcc = compute_mfcc(audio_path).mean(axis=1)  # Store mean as signature
        database[video_path] = mfcc
        temp[video_path] = mfcc.tolist()  # Convert to list for JSON serialization

    with open('database.json', 'w') as f:
        json.dump(temp, f)


def populate_database():
    """Loads the digital signatures from a JSON file into the database dictionary."""
    with open('./Digital Signatures/Integrated/sound_database.json') as f:
        data = json.load(f)
        for key in data.keys():
            database[key] = np.array(data[key])


def normalize_signature(signature):
    norm = np.linalg.norm(signature)
    if norm == 0:
        return signature
    return signature / norm


def find_best_three_matches(query_signature):
    query_signature = normalize_signature(query_signature)
    # Initialize matches and distances with high values
    matches = [None, None, None]
    distances = [float('inf'), float('inf'), float('inf')]

    for video_path, signature in database.items():
        normalized_signature = normalize_signature(signature)
        distance = np.linalg.norm(query_signature - normalized_signature)
        # Iterate through the sorted distances to place the current distance appropriately
        print(video_path, distance)
        for i in range(3):
            if distance < distances[i]:
                # Slide values down the list
                distances[i + 1:] = distances[i:-1]
                matches[i + 1:] = matches[i:-1]
                # Insert current distance and match
                distances[i] = distance
                matches[i] = video_path
                break
    return matches


def find_exact_frame(matched_video, query_mfcc, n_mfcc=13, hop_length=512, win_length=2048):
    """Finds the exact frame in the matched video that corresponds to the start of the query video."""
    if matched_video is None:
        return 1000000, 0
    y, sr = librosa.load(matched_video, sr=None)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc, hop_length=hop_length, win_length=win_length)
    #compare the two mfccs
    num_frames = mfccs.shape[1] - query_mfcc.shape[1] + 1
    min_distance = float('inf')
    best_frame_index = 0
    for i in range(num_frames):
        current_frame_mfcc = mfccs[:, i:i + query_mfcc.shape[1]]
        distance = np.linalg.norm(query_mfcc - current_frame_mfcc)
        if distance < min_distance:
            min_distance = distance
            best_frame_index = i
    frame_time = best_frame_index * hop_length / sr
    return min_distance, frame_time


def run_all_tests():
    for i in range(1, 11):
        run_single_test2(i)


def run_single_test(index):
    print("Query Video", index)
    time_start = timeit.default_timer()
    query_audio_path = "./Video Dataset/Query Videos/video" + str(index) + "_1_modified.wav"
    #query_audio_path = "./Video Dataset/Query Videos/video7alt2_1_modified.wav"
    query_mfcc = compute_mfcc(query_audio_path)
    best_match, second_match, third_match = find_best_three_matches(query_mfcc.mean(axis=1))
    min_val, frame_time = find_exact_frame(best_match, query_mfcc)
    #best_match = "./Video Dataset/video7.wav"
    min_val, frame_time = find_exact_frame(best_match, query_mfcc)
    min_val2, frame_time2 = find_exact_frame(second_match, query_mfcc)
    min_val3, frame_time3 = find_exact_frame(third_match, query_mfcc)
    print("Initial Best Match:", best_match, min_val)
    print("Initial Second Best Match:", second_match, min_val2)
    print("Initial Third Best Match:", third_match, min_val3)
    # Compare the min vals and which one is best
    actual_min = min(min_val, min_val2, min_val3)
    if actual_min == min_val:
        best_match = best_match
        frame_time = frame_time
    elif actual_min == min_val2:
        best_match = second_match
        frame_time = frame_time2
    else:
        best_match = third_match
        frame_time = frame_time3
    print("Matched Video:", best_match)
    print("Query starts at time:", frame_time, "seconds")
    # Print in minutes and seconds
    minutes = int(frame_time // 60)
    # Round seconds to the nearest integer
    seconds = int(round(frame_time % 60))
    print("Query starts at time:", minutes, "minutes and", seconds, "seconds")
    frame_index = int(frame_time * 30)  # 30 FPS
    # Print time elasped for each query video
    print("Time Elapsed: ", timeit.default_timer() - time_start)
    print("Query starts at frame index:", frame_index)


# This function finds the exact frame, prints it, and returns the frame index
# The Index refers to the original video index
def run_single_test2(query_path, original_index):
    video_template_string = "./static/Videos/video" + str(original_index) + ".wav"
    # query_audio_path = "./Video Dataset/Query Videos/video" + str(query_index) + "_1_modified.wav"
    query_mfcc = compute_mfcc(query_path)
    min_val, frame_time = find_exact_frame(video_template_string, query_mfcc)
    # print("Query Video", query_index)
    # print("Matched Video:", video_template_string)
    # print("Query starts at time:", frame_time, "seconds")
    # Print in minutes and seconds
    # minutes = int(frame_time // 60)
    # Round seconds to the nearest integer
    # seconds = int(round(frame_time % 60))
    # print("Query starts at time:", minutes, "minutes and", seconds, "seconds")
    frame_index = int(frame_time * 30)  # 30 FPS
    # print("Query starts at frame index:", frame_index)
    return frame_index+2, min_val


# Function to run tests on a list of video indices
def run_tests(query_path, video_indices):
    audio_score = {}
    for index in video_indices:
        audio_score[index] = run_single_test2(query_path, index)
    return audio_score


def audio(query_path, video_list):
    # populate_database()
    return run_tests(query_path, video_list)

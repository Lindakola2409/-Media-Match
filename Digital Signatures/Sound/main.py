import json
import numpy as np
import librosa
from moviepy.editor import VideoFileClip
from scipy.spatial.distance import cosine
from fastdtw import fastdtw

database = {
    "../../Video Dataset/video1.mp4": None,
    "../../Video Dataset/video2.mp4": None,
    "../../Video Dataset/video3.mp4": None,
    "../../Video Dataset/video4.mp4": None,
    "../../Video Dataset/video5.mp4": None,
    "../../Video Dataset/video6.mp4": None,
    "../../Video Dataset/video7.mp4": None,
    "../../Video Dataset/video8.mp4": None,
    "../../Video Dataset/video9.mp4": None,
    "../../Video Dataset/video10.mp4": None,
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
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    return mfcc  # Return the full MFCC array, not just the mean.


def preprocess_database():
    """Preprocesses each video in the database to compute and store their digital signatures."""
    temp = {}
    for video_path in database.keys():
        audio_path = extract_audio_from_video(video_path)
        signature = compute_mfcc(audio_path).mean(axis=1)  # Store mean as signature
        database[video_path] = signature.tolist()  # Convert to list for JSON serialization
        temp[video_path] = signature.tolist()

    with open('database.json', 'w') as f:
        json.dump(temp, f)


def populate_database():
    """Loads the digital signatures from a JSON file into the database dictionary."""
    with open('database.json') as f:
        data = json.load(f)
        for key in data.keys():
            database[key] = np.array(data[key])


def normalize_signature(signature):
    norm = np.linalg.norm(signature)
    if norm == 0:
        return signature
    return signature / norm

def find_best_match(query_signature):
    query_signature = normalize_signature(query_signature)
    min_distance = float('inf')
    best_match = None
    for video_path, signature in database.items():
        normalized_signature = normalize_signature(signature)
        distance = np.linalg.norm(query_signature - normalized_signature)
        if distance < min_distance:
            min_distance = distance
            best_match = video_path
    return best_match

def find_exact_frame(matched_video, query_mfcc, hop_length=512, win_length=2048):
    """Finds the exact frame in the matched video that corresponds to the start of the query video."""
    audio_path = extract_audio_from_video(matched_video)
    y, sr = librosa.load(audio_path, sr=None)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=query_mfcc.shape[0], hop_length=hop_length, win_length=win_length)
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
    frame_time = int(round(frame_time))
    return frame_time


if __name__ == "__main__":
    preprocess_database()  # Uncomment this line to preprocess the database initially
    populate_database()
    query_video_path = "../../Video Dataset/Query Videos/video7_1_modified.mp4"
    query_audio_path = extract_audio_from_video(query_video_path)
    query_mfcc = compute_mfcc(query_audio_path)
    #matched_video = find_best_match(query_mfcc.mean(axis=1))
    matched_video = "../../Video Dataset/video7.mp4"
    frame_time = find_exact_frame(matched_video, query_mfcc)
    print("Matched Video:", matched_video)
    print("Query starts at time:", frame_time, "seconds")
    # Print in minutes and seconds
    minutes = int(frame_time // 60)
    # Round seconds to the nearest integer
    seconds = int(round(frame_time % 60))
    print("Query starts at time:", minutes, "minutes and", seconds, "seconds")
    frame_index = int(frame_time * 30)  # 30 FPS
    print("Query starts at frame index:", frame_index)
    # play_matched_video(matched_video)

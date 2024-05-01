import json
import numpy as np
import librosa
from moviepy.editor import VideoFileClip

# Initialize the database dictionary with video paths
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
    video = VideoFileClip(video_path)
    audio_path = video_path.replace('.mp4', '.wav')
    video.audio.write_audiofile(audio_path)
    return audio_path

def compute_features(audio_path):
    y, sr = librosa.load(audio_path, sr=None)
    rms = librosa.feature.rms(y=y)
    rms_mean = np.mean(rms)
    return rms_mean

def preprocess_database():
    """Preprocesses each video in the database to compute and store their RMS features."""
    temp = {}
    for video_path in database.keys():
        audio_path = extract_audio_from_video(video_path)
        rms_feature = compute_features(audio_path)
        # Ensure the rms_feature is a Python float, not numpy.float32
        rms_feature = float(rms_feature)
        database[video_path] = rms_feature
        temp[video_path] = rms_feature  # Store as a native Python float
    with open('database_rms.json', 'w') as f:
        json.dump(temp, f)

def populate_database():
    with open('database_rms.json') as f:
        data = json.load(f)
        for key in data.keys():
            database[key] = float(data[key])

def find_best_match(query_rms):
    min_distance = float('inf')
    best_match = None
    for video_path, rms_feature in database.items():
        distance = abs(query_rms - rms_feature)
        if distance < min_distance:
            min_distance = distance
            best_match = video_path
    return best_match

def main():
    #preprocess_database()
    populate_database()
    query_video_path = "../../Video Dataset/Query Videos/video7alt_1_modified.mp4"
    query_audio_path = extract_audio_from_video(query_video_path)
    query_rms = compute_features(query_audio_path)
    matched_video = find_best_match(query_rms)
    print("Matched Video:", matched_video)

if __name__ == "__main__":
    main()
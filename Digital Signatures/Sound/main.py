import numpy as np
import librosa
from moviepy.editor import VideoFileClip

database = {
    "video1.mp4": None,
    "video2.mp4": None,
    "video3.mp4": None,
}


def extract_audio_from_video(video_path):
    """Extracts audio from the video file and returns the path to the temporary audio file."""
    video = VideoFileClip(video_path)
    audio_path = video_path.replace('.mp4', '.wav')  # Create a corresponding WAV filename
    video.audio.write_audiofile(audio_path)
    return audio_path


def compute_mfcc(audio_path, n_mfcc=13):
    """Computes the MFCCs of the audio file and returns a mean vector as the digital signature."""
    y, sr = librosa.load(audio_path, sr=None)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    mfcc_mean = np.mean(mfcc, axis=1)
    return mfcc_mean


def preprocess_database():
    """Preprocesses each video in the database to compute and store their digital signatures."""
    for video_path in database.keys():
        audio_path = extract_audio_from_video(video_path)
        signature = compute_mfcc(audio_path)
        database[video_path] = signature


def find_best_match(query_signature):
    """Finds the closest match in the database by comparing signatures."""
    min_distance = float('inf')
    best_match = None
    for video_path, signature in database.items():
        distance = np.linalg.norm(query_signature - signature)
        if distance < min_distance:
            min_distance = distance
            best_match = video_path
    return best_match


def play_matched_video(video_path):
    """Plays the matched video."""
    clip = VideoFileClip(video_path)
    clip.preview()


# Example usage
preprocess_database()
query_video_path = "query_video.mp4"
query_audio_path = extract_audio_from_video(query_video_path)
query_signature = compute_mfcc(query_audio_path)
matched_video = find_best_match(query_signature)
print("Matched Video:", matched_video)
play_matched_video(matched_video)

from moviepy.editor import VideoFileClip


# create wav file from video
def extract_audio_from_video(video_path):
    video = VideoFileClip(video_path)
    audio_path = video_path.replace('.mp4', '.wav')
    video.audio.write_audiofile(audio_path)
    return audio_path

def extract_audio_from_all_original_videos():
    original_video_paths = [
        "../../Video Dataset/video1.mp4",
        "../../Video Dataset/video2.mp4",
        "../../Video Dataset/video3.mp4",
        "../../Video Dataset/video4.mp4",
        "../../Video Dataset/video5.mp4",
        "../../Video Dataset/video6.mp4",
        "../../Video Dataset/video7.mp4",
        "../../Video Dataset/video8.mp4",
        "../../Video Dataset/video9.mp4",
        "../../Video Dataset/video10.mp4",
        "../../Video Dataset/video11.mp4",
        "../../Video Dataset/video12.mp4",
        "../../Video Dataset/video13.mp4",
        "../../Video Dataset/video14.mp4",
        "../../Video Dataset/video15.mp4",
        "../../Video Dataset/video16.mp4",
        "../../Video Dataset/video17.mp4",
        "../../Video Dataset/video18.mp4",
        "../../Video Dataset/video19.mp4",
        "../../Video Dataset/video20.mp4",
    ]
    audio_paths = []
    for video_path in original_video_paths:
        audio_path = extract_audio_from_video(video_path)
        audio_paths.append(audio_path)
    return audio_paths

def extract_audio_from_all_query_videos():
    query_video_paths = [
        "../../Video Dataset/Query Videos/video1_1_modified.mp4",
        "../../Video Dataset/Query Videos/video2_1_modified.mp4",
        "../../Video Dataset/Query Videos/video3_1_modified.mp4",
        "../../Video Dataset/Query Videos/video4_1_modified.mp4",
        "../../Video Dataset/Query Videos/video5_1_modified.mp4",
        "../../Video Dataset/Query Videos/video6_1_modified.mp4",
        "../../Video Dataset/Query Videos/video7_1_modified.mp4",
        "../../Video Dataset/Query Videos/video8_1_modified.mp4",
        "../../Video Dataset/Query Videos/video9_1_modified.mp4",
        "../../Video Dataset/Query Videos/video10_1_modified.mp4",
    ]
    audio_paths = []
    for video_path in query_video_paths:
        audio_path = extract_audio_from_video(video_path)
        audio_paths.append(audio_path)
    return audio_paths

def main():
    extract_audio_from_all_original_videos()
    extract_audio_from_all_query_videos()


if __name__ == "__main__":
    main()

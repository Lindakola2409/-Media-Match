from moviepy.editor import VideoFileClip


# create wav file from video
def extract_audio_from_video(video_path):
    video = VideoFileClip(video_path)
    audio_path = video_path.replace('.mp4', '.wav')
    video.audio.write_audiofile(audio_path)
    return audio_path


def main():
    query_video_path = "../../Video Dataset/Query Videos/video7alt2_1_modified.mp4"
    path = extract_audio_from_video(query_video_path)
    print(path)


if __name__ == "__main__":
    main()

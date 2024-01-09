from moviepy.editor import VideoFileClip
import os


def extract_screenshot(video_path):
    # Load the video clip
    video_clip = VideoFileClip(video_path)
    file_name = video_clip.filename + ",jpg"

    # Save the screenshot as an image file
    video_clip.save_frame(file_name, t=10)

    return file_name

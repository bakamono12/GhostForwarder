from moviepy.editor import VideoFileClip
import os


def extract_screenshot(video_path):
    # Load the video clip
    video_clip = VideoFileClip(video_path)
    file_name = video_clip.filename + ".jpg"
    width, height = video_clip.size
    duration = video_clip.duration

    # Save the screenshot as an image file
    video_clip.save_frame(file_name, t=10)

    return width, height, duration


if __name__ == "__main__":
    a, b, c = extract_screenshot("honey_bee_busy_insect_flower_bee_659.mp4")
    print(a, b, c)

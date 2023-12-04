from moviepy.video.io.VideoFileClip import VideoFileClip


def generate_thumbnail(video_path, thumbnail_path, time_in_seconds=10):
    # Load the video clip
    video_clip = VideoFileClip(video_path)
    # Save the frame as an image (thumbnail)
    video_clip.save_frame(thumbnail_path, t=time_in_seconds)

    # Close the video clip
    video_clip.close()

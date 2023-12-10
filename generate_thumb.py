import cv2
import os


def generate_thumbnail(file_path):
    """Generate a dynamically sized thumbnail from an image or video file"""
    _, file_extension = os.path.splitext(file_path.lower())
    if file_extension in {'.mp4', '.avi', '.mkv', '.webm', '.mov', '.flv', '.wmv', '.gif'}:
        # For video files only
        return video_to_thumbnail(file_path)
    else:
        print("Unsupported file format.")
        return None


def video_to_thumbnail(video_filename):
    """Extract a single thumbnail from video"""
    cap = cv2.VideoCapture(video_filename)
    if not cap.isOpened():
        return None

    # Get the frame at the middle of the video
    mid_frame_id = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / 2)

    cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame_id)
    success, image = cap.read()

    cap.release()  # Release the video capture object

    if not success:
        return None
    else:
        # Save the frame as an image file
        cv2.imwrite(video_filename + ".jpg", image)
    return image



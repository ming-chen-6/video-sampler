import cv2


def load_video(path):
    """Returns cv2 VideoCapture object."""
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {path}")
    return cap


def get_video_info(cap):
    """Returns dict with fps, frame_count, duration, resolution."""
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = frame_count / fps if fps > 0 else 0

    return {
        "fps": fps,
        "frame_count": frame_count,
        "duration": duration,
        "resolution": (width, height)
    }

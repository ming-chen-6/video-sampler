import cv2
from .video_utils import load_video, get_video_info
from .export import save_frame


def sample_video(video_path, output_folder, mode, interval=None, points=None, resize=None):
    """
    Sample frames from video.
    mode: "seconds" or "frames"
    interval: int/float for regular sampling
    points: list for specific timestamps/frames
    Returns list of saved file paths.
    """
    cap = load_video(video_path)
    info = get_video_info(cap)
    fps = info["fps"]
    frame_count = info["frame_count"]

    # Determine which frames to extract
    if points is not None:
        if mode == "seconds":
            target_frames = [int(t * fps) for t in points]
        else:
            target_frames = [int(f) for f in points]
    elif interval is not None:
        if mode == "seconds":
            frame_interval = int(interval * fps)
        else:
            frame_interval = int(interval)
        target_frames = list(range(0, frame_count, frame_interval))
    else:
        raise ValueError("Either interval or points must be provided")

    # Filter valid frames
    target_frames = [f for f in target_frames if 0 <= f < frame_count]

    saved_paths = []
    for idx, frame_num in enumerate(target_frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        if ret:
            path = save_frame(frame, output_folder, idx, resize)
            saved_paths.append(path)

    cap.release()
    return saved_paths

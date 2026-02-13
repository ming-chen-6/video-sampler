import cv2
import shutil
import subprocess
from pathlib import Path
from .video_utils import load_video, get_video_info
from .export import save_frame, _frame_label


def _ffmpeg_available():
    """Check if ffmpeg is in PATH."""
    return shutil.which("ffmpeg") is not None


def sample_video(video_path, output_folder, mode, interval=None, points=None, resize=None, parallel=None):
    """
    Sample frames from video.
    mode: "seconds" or "frames"
    interval: int/float for regular sampling
    points: list for specific timestamps/frames
    parallel: None=cv2 sequential, int=ffmpeg parallel (falls back to cv2 if ffmpeg unavailable)
    Returns list of saved file paths.
    """
    if parallel and _ffmpeg_available():
        return _sample_ffmpeg(video_path, output_folder, mode, interval, points, resize, parallel)
    if parallel and not _ffmpeg_available():
        print("ffmpeg not found, falling back to cv2")
    return _sample_cv2(video_path, output_folder, mode, interval, points, resize)


def _sample_cv2(video_path, output_folder, mode, interval=None, points=None, resize=None):
    """CV2-based sequential sampling."""
    cap = load_video(video_path)
    info = get_video_info(cap)
    fps = info["fps"]
    frame_count = info["frame_count"]

    target_frames = _get_target_frames(mode, interval, points, fps, frame_count)
    total = len(target_frames)

    saved_paths = []
    for idx, frame_num in enumerate(target_frames):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        ret, frame = cap.read()
        if ret:
            path = save_frame(frame, output_folder, idx, resize, frame_num=frame_num, fps=fps, mode=mode)
            saved_paths.append(path)
        # Progress
        print(f"\rProcessing: {idx + 1}/{total}", end="", flush=True)

    cap.release()
    return saved_paths


def _sample_ffmpeg(video_path, output_folder, mode, interval=None, points=None, resize=None, threads=4):
    """FFmpeg-based parallel sampling."""
    cap = load_video(video_path)
    info = get_video_info(cap)
    fps = info["fps"]
    frame_count = info["frame_count"]
    cap.release()

    output_pattern = str(Path(output_folder) / "frame_%06d.png")

    # Build ffmpeg command
    cmd = ["ffmpeg", "-i", str(video_path), "-threads", str(threads)]

    # Build filter chain
    filters = []

    if points is not None:
        # Specific frames/timestamps - use select filter
        if mode == "seconds":
            # Convert seconds to frame numbers
            frame_points = [int(t * fps) for t in points]
        else:
            frame_points = [int(f) for f in points]
        expr = "+".join([f"eq(n,{f})" for f in frame_points])
        filters.append(f"select='{expr}'")
    elif interval is not None:
        # Regular interval - match cv2 logic exactly
        if mode == "seconds":
            frame_interval = int(interval * fps)
        else:
            frame_interval = int(interval)
        filters.append(f"select='not(mod(n,{frame_interval}))'")

    # Add resize if specified
    if resize is not None:
        if isinstance(resize, (int, float)):
            filters.append(f"scale=iw*{resize}:ih*{resize}")
        else:
            filters.append(f"scale={resize[0]}:{resize[1]}")

    if filters:
        cmd.extend(["-vf", ",".join(filters)])

    cmd.extend(["-vsync", "vfr", output_pattern])

    print("Processing with ffmpeg...", end="", flush=True)
    subprocess.run(cmd, capture_output=True, check=True)
    print(" done")

    # Rename files to include time/frame labels
    target_frames = _get_target_frames(mode, interval, points, fps, frame_count)
    saved = sorted(Path(output_folder).glob("frame_*.png"))
    renamed = []
    for idx, path in enumerate(saved):
        if idx < len(target_frames):
            label = _frame_label(target_frames[idx], fps, mode)
            new_name = path.parent / f"frame_{idx:06d}_{label}.png"
            path.rename(new_name)
            renamed.append(new_name)
        else:
            renamed.append(path)
    return renamed


def _get_target_frames(mode, interval, points, fps, frame_count):
    """Calculate target frame numbers."""
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

    return [f for f in target_frames if 0 <= f < frame_count]

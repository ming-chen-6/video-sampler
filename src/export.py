from pathlib import Path
from datetime import datetime
import cv2


def create_output_folder(name):
    """Creates output/{name}_{YYYYMMDD_HHMM}/, returns Path."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    folder = Path("output") / f"{name}_{timestamp}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def resize_frame(frame, resize):
    """Resize frame. None=original, float=scale factor, tuple=(w,h)."""
    if resize is None:
        return frame
    if isinstance(resize, (int, float)):
        return cv2.resize(frame, None, fx=resize, fy=resize)
    return cv2.resize(frame, resize)


def _frame_label(frame_num, fps, mode):
    """Generate a label like '1m42s' (seconds mode) or '1424f' (frames mode)."""
    if mode == "seconds":
        total_sec = frame_num / fps
        minutes = int(total_sec // 60)
        seconds = int(total_sec % 60)
        return f"{minutes}m{seconds:02d}s"
    else:
        return f"{frame_num}f"


def save_frame(frame, folder, index, resize=None, frame_num=None, fps=None, mode=None):
    """Saves frame as PNG. Includes time/frame label in name when info is provided."""
    frame = resize_frame(frame, resize)
    if frame_num is not None and fps is not None and mode is not None:
        label = _frame_label(frame_num, fps, mode)
        filename = folder / f"frame_{index:06d}_{label}.png"
    else:
        filename = folder / f"frame_{index:06d}.png"
    cv2.imwrite(str(filename), frame)
    return filename

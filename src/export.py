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


def save_frame(frame, folder, index, resize=None):
    """Saves frame as PNG with zero-padded name."""
    frame = resize_frame(frame, resize)
    filename = folder / f"frame_{index:06d}.png"
    cv2.imwrite(str(filename), frame)
    return filename

"""
Shared input validation helpers for AI Skin Specialist.

This module validates audio, image, and video paths before they are sent to
external APIs. It is intentionally small and beginner-friendly.

Validation checks:
- File exists and is a regular file
- File is readable
- File has an allowed extension for its media type
- File is large enough to be a real upload (not empty/corrupt placeholder)

It does NOT try to open audio or video files, because the current app does not
need that and we want to keep dependencies and complexity low.

Validation failures are reported as ValueError with user-facing messages suitable
for Gradio, not as raw tracebacks.
"""

from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Optional, Set

logger = logging.getLogger("ai_skin_specialist")


# Allowed extensions for each media type.
# These are intentionally conservative subsets of what Gradio might accept.
ALLOWED_AUDIO_EXTENSIONS: Set[str] = {".wav", ".mp3", ".ogg", ".m4a", ".webm"}
ALLOWED_IMAGE_EXTENSIONS: Set[str] = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_VIDEO_EXTENSIONS: Set[str] = {".mp4", ".webm", ".mov", ".avi"}

# Minimum file size in bytes. Files smaller than this are likely empty or corrupt
# uploads and should be rejected early rather than failing later inside an API call.
MIN_FILE_SIZE_BYTES = 1024  # 1 KB


def _normalize_extension(path: Path) -> str:
    """
    Return the lowercased file extension, including the leading dot.

    Unknown extensions are returned as-is so callers can decide whether to reject
    them. This keeps the function predictable for both recognized and unrecognized
    file types.
    """
    return path.suffix.lower()


def _is_allowed_extension(path: Path, allowed: Set[str]) -> bool:
    """
    Check whether the file extension is in the allowed set.
    """
    return _normalize_extension(path) in allowed


def _is_file_readable(path: Path) -> bool:
    """
    Check whether the path exists, is a regular file, and can be opened for reading.
    """
    if not path.exists():
        return False
    if not path.is_file():
        return False
    try:
        with path.open("rb"):
            pass
        return True
    except OSError:
        return False


def _is_file_large_enough(path: Path, min_size: int = MIN_FILE_SIZE_BYTES) -> bool:
    """
    Check whether the file is at least min_size bytes.
    """
    try:
        return path.stat().st_size >= min_size
    except OSError:
        return False


def validate_media_path(
    filepath: Optional[str],
    allowed_extensions: Set[str],
    media_kind: str,
    min_size: int = MIN_FILE_SIZE_BYTES,
) -> Path:
    """
    Validate a generic media file path before it is used by the pipeline.

    This is the shared validator used by audio, image, and video checks. It confirms:

    - A path was actually provided.
    - The path looks like a real file path (string or Path-like).
    - The file exists and is a readable regular file.
    - The file extension is in the allowed set for the given media kind.
    - The file is large enough to be a real upload and not an empty/corrupt placeholder.

    Args:
        filepath: The file path from the UI, as a string or None.
        allowed_extensions: Set of permitted extensions for this media kind.
        media_kind: Human-readable label used in error messages, e.g. "audio",
                    "image", or "video".
        min_size: Minimum acceptable file size in bytes.

    Returns:
        The validated path as a Path object.

    Raises:
        ValueError: With a user-friendly message if any check fails.
    """
    if filepath is None or not isinstance(filepath, str) or filepath.strip() == "":
        raise ValueError(f"Please provide a {media_kind} file before analysis.")

    path = Path(filepath)

    if not _is_file_readable(path):
        raise ValueError(
            f"The provided {media_kind} file could not be read. "
            "Please record or upload a valid {media_kind} file and try again.".format(
                media_kind=media_kind
            )
        )

    if not _is_allowed_extension(path, allowed_extensions):
        raise ValueError(
            f"The {media_kind} file has an unsupported format. "
            "Please upload a supported {media_kind} file.".format(media_kind=media_kind)
        )

    if not _is_file_large_enough(path, min_size):
        raise ValueError(
            f"The {media_kind} file appears to be empty or too small. "
            "Please provide a complete {media_kind} recording or file.".format(
                media_kind=media_kind
            )
        )

    return path


def validate_audio_path(filepath: Optional[str]) -> Path:
    """
    Validate an audio path from the UI.

    Delegates to validate_media_path with the allowed audio extensions.

    Returns the validated Path on success.
    Raises ValueError with a user-friendly message on failure.
    """
    return validate_media_path(
        filepath=filepath,
        allowed_extensions=ALLOWED_AUDIO_EXTENSIONS,
        media_kind="audio",
    )


def validate_image_path(filepath: Optional[str]) -> Path:
    """
    Validate an image path from the UI.

    In addition to the generic media checks, this confirms the file can be opened as
    an image by Pillow, since the vision backend relies on that.

    Returns the validated Path on success.
    Raises ValueError with a user-friendly message on failure.
    """
    path = validate_media_path(
        filepath=filepath,
        allowed_extensions=ALLOWED_IMAGE_EXTENSIONS,
        media_kind="image",
    )

    # Extra image-specific check: confirm Pillow can open it. This catches files that
    # have a valid image extension but are not actually readable as images.
    try:
        from PIL import Image

        with Image.open(path) as _image:
            _image.verify()
        # Image.open with verify() does not fully read the file, so reopen to
        # confirm it is a valid, complete image that can be decoded.
        with Image.open(path) as _image:
            _image.load()
    except Exception as exc:
        logger.warning("Image validation failed for %s: %s", path, type(exc).__name__)
        raise ValueError(
            "The provided image file could not be read as an image. "
            "Please upload a valid image file and try again."
        ) from None

    return path


def validate_video_path(filepath: Optional[str]) -> Path:
    """
    Validate a video path from the UI.

    The current Groq vision backend does not actually process video, but the UI still
    accepts a video input. This validator performs basic sanity checks on the video
    path but does NOT attempt to open or decode the video, because that would require
    additional dependencies and is not needed by the active backend.

    Returns the validated Path on success.
    Raises ValueError with a user-friendly message on failure.
    """
    return validate_media_path(
        filepath=filepath,
        allowed_extensions=ALLOWED_VIDEO_EXTENSIONS,
        media_kind="video",
    )

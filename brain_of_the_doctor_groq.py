import base64
import os
from io import BytesIO
from pathlib import Path

import cv2
from dotenv import load_dotenv
from groq import Groq
from PIL import Image

from app_logging import get_logger

load_dotenv()

_logger = get_logger("brain_of_the_doctor_groq")

DEFAULT_MODEL = "qwen/qwen3.8-27b"
MAX_IMAGE_SIZE = (1024, 1024)
MAX_VIDEO_FRAMES = 3


def _has_api_key() -> bool:
    """Check whether the Groq API key is present."""
    return bool(os.environ.get("GROQ_API_KEY"))


def _encode_pil_image(image):
    """Convert a PIL image into a base64 JPEG string."""

    image.thumbnail(MAX_IMAGE_SIZE)

    buffer = BytesIO()

    image.convert("RGB").save(
        buffer,
        format="JPEG",
        quality=75
    )

    return base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")


def encode_image_for_groq(filepath):
    """Encode an uploaded image for Groq vision."""

    path = Path(filepath)

    if not path.exists() or not path.is_file():
        raise ValueError(
            "The image file was not found. Please upload a valid skin image."
        )

    try:
        with Image.open(path) as image:
            image_data = _encode_pil_image(image.copy())

        _logger.info(
            "Image encoded for Groq vision: %s",
            path.name
        )

        return image_data

    except ValueError:
        raise

    except Exception as exc:
        _logger.warning(
            "Image encoding failed: %s",
            type(exc).__name__
        )

        raise ValueError(
            "The uploaded image could not be processed. "
            "Please upload another image."
        ) from None


def extract_video_frames(filepath, max_frames=MAX_VIDEO_FRAMES):
    """
    Extract representative frames from an uploaded video.

    Frames are sampled at evenly distributed positions.
    The function returns base64 JPEG images.
    """

    path = Path(filepath)

    if not path.exists() or not path.is_file():
        raise ValueError(
            "The video file was not found. Please upload a valid video."
        )

    capture = cv2.VideoCapture(str(path))

    if not capture.isOpened():
        raise ValueError(
            "The uploaded video could not be opened. "
            "Please try another video."
        )

    try:
        total_frames = int(
            capture.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        if total_frames <= 0:
            raise ValueError(
                "No readable frames were found in the uploaded video."
            )

        # Select evenly distributed frame positions.
        frame_count = min(max_frames, total_frames)

        if frame_count == 1:
            frame_indices = [0]
        else:
            frame_indices = [
                round(
                    index * (total_frames - 1) /
                    (frame_count - 1)
                )
                for index in range(frame_count)
            ]

        encoded_frames = []

        for frame_number in frame_indices:

            capture.set(
                cv2.CAP_PROP_POS_FRAMES,
                frame_number
            )

            success, frame = capture.read()

            if not success or frame is None:
                _logger.warning(
                    "Could not read video frame: %s",
                    frame_number
                )
                continue

            # OpenCV uses BGR; PIL expects RGB.
            frame_rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            pil_image = Image.fromarray(frame_rgb)

            encoded_frame = _encode_pil_image(
                pil_image
            )

            encoded_frames.append(encoded_frame)

        if not encoded_frames:
            raise ValueError(
                "No usable frames could be extracted from the video."
            )

        _logger.info(
            "Extracted %s video frames from %s",
            len(encoded_frames),
            path.name
        )

        return encoded_frames

    finally:
        capture.release()


def brain_of_the_doctor(
    patient_text,
    image_filepath=None,
    video_filepath=None
):
    """
    Generate general skin-care information using Groq vision.

    Supports:
    - Image only
    - Video only
    - Image and video together
    """

    if not _has_api_key():
        raise ValueError(
            "Groq vision is not configured. "
            "Please set GROQ_API_KEY in your .env file."
        )

    if not image_filepath and not video_filepath:
        raise ValueError(
            "Please upload a skin image or video."
        )

    # -------------------------------------------------
    # Step 1: Prepare visual inputs.
    # -------------------------------------------------

    image_data_list = []

    if image_filepath:

        image_data = encode_image_for_groq(
            image_filepath
        )

        image_data_list.append(image_data)

    if video_filepath:

        # The model supports a maximum of 3 images.
        # Reserve one slot for the uploaded image if present.
        available_video_slots = (
            MAX_VIDEO_FRAMES - len(image_data_list)
        )

        if available_video_slots > 0:

            video_frames = extract_video_frames(
                video_filepath,
                max_frames=available_video_slots
            )

            image_data_list.extend(video_frames)

    if not image_data_list:
        raise ValueError(
            "No usable visual information was found. "
            "Please upload another image or video."
        )

    # -------------------------------------------------
    # Step 2: Prepare the AI prompt.
    # -------------------------------------------------

    prompt = (
        "You are a careful skin-care information assistant. "
        "Review the patient's description and all supplied visual inputs. "
        "The visual inputs may include a still image and selected frames "
        "extracted from a video. "
        "Consider the visible area, lighting, and differences between "
        "the selected video frames when providing general observations. "
        "Do not claim to provide a medical diagnosis. "
        "Do not invent symptoms or visual details that cannot be confirmed. "
        "If the available images are unclear, mention this limitation. "
        "Give a helpful response in two or three short sentences. "
        "Avoid markdown formatting because the response will be converted "
        "into speech.\n\n"
        f"Patient description: {patient_text}"
    )

    # -------------------------------------------------
    # Step 3: Send visual inputs to Groq.
    # -------------------------------------------------

    try:

        client = Groq(
            api_key=os.environ["GROQ_API_KEY"]
        )

        model_name = os.environ.get(
            "GROQ_MODEL",
            DEFAULT_MODEL
        )

        message_content = [
            {
                "type": "text",
                "text": prompt
            }
        ]

        for index, image_data in enumerate(
            image_data_list,
            start=1
        ):

            message_content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": (
                            f"data:image/jpeg;base64,{image_data}"
                        )
                    }
                }
            )

            _logger.info(
                "Added visual input %s to Groq request",
                index
            )

        _logger.info(
            "Sending image/video analysis using model: %s",
            model_name
        )

        response = client.chat.completions.create(
            model=model_name,
            max_completion_tokens=1000,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful skin-care information "
                        "assistant. Provide general information, "
                        "not a medical diagnosis. Never claim certainty "
                        "from images alone."
                    )
                },
                {
                    "role": "user",
                    "content": message_content
                }
            ]
        )

        content = response.choices[0].message.content

        if not content or not str(content).strip():

            _logger.warning(
                "Groq returned an empty response"
            )

            raise ValueError(
                "The analysis returned no guidance. "
                "Please try again."
            )

        _logger.info(
            "Groq vision analysis completed successfully"
        )

        return content

    except ValueError:
        raise

    except Exception as exc:

        _logger.exception(
            "Groq vision request failed: %s",
            type(exc).__name__
        )

        raise ValueError(
            "The skin analysis service encountered an API error. "
            "Please check the terminal logs."
        ) from None
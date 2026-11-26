import os
from pathlib import Path

from dotenv import load_dotenv
from deepgram import DeepgramClient

from app_logging import get_logger

load_dotenv()

_logger = get_logger("voice_of_the_doctor")

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DOCTOR_AUDIO = BASE_DIR / "doctor_response.mp3"


def convert_text_to_doctor_audio(text, output_filepath=DEFAULT_DOCTOR_AUDIO):
    """
    Convert the doctor's text response into spoken audio using Deepgram TTS.
    """

    if not text:
        raise ValueError(
            "No text was provided to convert to audio. Please try again."
        )

    deepgram_api_key = os.environ.get("DEEPGRAM_API_KEY")

    if not deepgram_api_key:
        raise ValueError(
            "Text-to-speech is not configured. Please set DEEPGRAM_API_KEY."
        )

    output_path = Path(output_filepath)

    try:
        deepgram = DeepgramClient(api_key=deepgram_api_key)

        audio = deepgram.speak.v1.audio.generate(
            text=text,
            model=os.environ.get(
                "DEEPGRAM_TTS_MODEL",
                "aura-2-thalia-en"
            ),
            encoding="mp3",
        )

        with output_path.open("wb") as file:
            for chunk in audio:
                file.write(chunk)

        _logger.info(
            "Deepgram TTS audio saved to %s",
            output_path.name
        )

        return output_path

    except ValueError:
        raise

    except Exception as exc:
        _logger.warning(
            "Deepgram TTS generation failed: %s",
            type(exc).__name__
        )

        raise ValueError(
            "Could not generate the doctor's voice response. "
            "Please try again in a moment."
        ) from None
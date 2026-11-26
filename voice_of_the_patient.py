import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from app_logging import get_logger


load_dotenv()

_logger = get_logger("voice_of_the_patient")

WHISPER_MODEL = os.getenv(
    "WHISPER_MODEL",
    "whisper-large-v3"
)


def transcribe_patient_voice(audio_filepath):

    if not audio_filepath:
        raise ValueError("Please provide an audio recording.")

    if not os.getenv("GROQ_API_KEY"):
        raise ValueError("GROQ_API_KEY is not configured.")

    audio_path = Path(audio_filepath)

    if not audio_path.exists() or not audio_path.is_file():
        raise ValueError("The uploaded audio file could not be found.")

    if audio_path.stat().st_size == 0:
        raise ValueError("The uploaded audio file is empty.")

    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        with audio_path.open("rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model=WHISPER_MODEL,
                file=audio_file,
                response_format="text"
            )

        transcript = (
            transcription
            if isinstance(transcription, str)
            else getattr(transcription, "text", "")
        )

        transcript = transcript.strip()

        if not transcript:
            raise ValueError("No speech could be detected in the audio.")

        _logger.info("Patient voice transcription completed successfully.")

        return transcript

    except ValueError:
        raise

    except Exception as exc:
        _logger.error(
            "Patient voice transcription failed: %s",
            type(exc).__name__
        )

        raise ValueError(
            "Unable to transcribe the audio. Please try again."
        ) from None
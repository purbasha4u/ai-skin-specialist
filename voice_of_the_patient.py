# Step1: Record audio from microphone

# dependencies: ffmpeg, portaudio, pyaudio (commands available in description)
import logging
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def record_audio(file_path, timeout=20, phrase_time_limit=None):
    """
    Simplified function to record audio from the microphone and save it as an MP3 file.

    Args:
    file_path (str): Path to save the recorded audio file.
    timeout (int): Maximum time to wait for a phrase to start (in seconds).
    phrase_time_lfimit (int): Maximum time for the phrase to be recorded (in seconds).
    """
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        logging.info("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        logging.info("Start speaking now...")
        
        # Record the audio
        audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        logging.info("Recording complete.")
        
        # Convert the recorded audio to an MP3 file
        wav_data = audio_data.get_wav_data()
        audio_segment = AudioSegment.from_wav(BytesIO(wav_data))
        audio_segment.export(file_path, format="mp3", bitrate="128k")
        
        logging.info(f"Audio saved to {file_path}")

audio_filepath="patient_voice_test.mp3"
#record_audio(audio_filepath, timeout=20, phrase_time_limit=10)


# Step2: Convert audio to text
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from app_logging import get_logger

load_dotenv()

_logger = get_logger("voice_of_the_patient")


def _safe_read_text(value: str, label: str) -> str:
    """
    Return the value if it looks usable, otherwise raise a ValueError suitable
    for end-user messaging.

    We do NOT log the actual content here because it may be a patient transcript.
    """
    if value is None:
        raise ValueError(f"{label} returned no text. Please try again.")
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{label} returned empty text. Please try again.")
    return stripped


def transcribe_patient_voice(audio_filepath):
    """
    Transcribe patient voice audio using Groq Whisper.

    On failure, this raises a ValueError with a user-friendly message instead of
    letting a raw exception bubble up to the UI.

    We intentionally do NOT log the audio file path or transcript content here;
    they may be patient data. Only the failure type and a short diagnostic are logged.
    """
    groq_api_key = os.environ.get("GROQ_API_KEY")

    if not groq_api_key:
        raise ValueError(
            "Transcription is not configured. Please set GROQ_API_KEY in your environment or .env file."
        )

    # Confirm the file exists before trying to send it.
    path = Path(audio_filepath)
    if not path.exists():
        raise ValueError("The recorded audio file was not found. Please record again and try again.")
    if not path.is_file():
        raise ValueError("The audio path is not a file. Please record again and try again.")

    try:
        client = Groq(api_key=groq_api_key)
        with open(audio_filepath, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model=os.environ.get("WHISPER_MODEL", "whisper-large-v3"),
            )

        patient_text = _safe_read_text(getattr(transcription, "text", None), "Transcription")
        _logger.info("Whisper transcription completed successfully")
        return patient_text

    except ValueError:
        # re-raise user-facing validation errors as-is
        raise
    except Exception as exc:
        _logger.warning("Groq Whisper transcription failed: %s", type(exc).__name__)
        raise ValueError(
            "Could not transcribe your voice. Please make sure the audio is clear and try again."
        ) from None
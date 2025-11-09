"""Fallback STT service using OpenAI Whisper directly when MCP is not available."""
import logging
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)


def transcribe_with_openai(file_path: str) -> str:
    """
    Transcribe audio using OpenAI Whisper API.
    
    Uses Whisper-1 model for high-quality speech-to-text transcription.
    
    Args:
        file_path: Path to audio file (webm, mp3, wav, etc.)
    
    Returns:
        Transcribed text
    """
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY not configured. Cannot use Whisper API.")
    
    try:
        # Clean API key (remove any whitespace)
        api_key = settings.openai_api_key.strip()
        
        if not api_key or len(api_key) < 20:
            raise ValueError("Invalid API key format. Key appears to be empty or too short.")
        
        client_kwargs = {"api_key": api_key}
        if settings.openai_project_id:
            client_kwargs["default_headers"] = {
                "OpenAI-Project": settings.openai_project_id
            }

        client = OpenAI(**client_kwargs)
        
        logger.info(f"Transcribing audio with Whisper from file: {file_path}")
        
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",  # OpenAI Whisper model
                file=audio_file,
                language="en",  # Optional: specify language for better accuracy
                response_format="text"  # Get plain text response
            )
        
        # Handle both string and object responses
        if isinstance(transcript, str):
            transcript_text = transcript
        else:
            transcript_text = transcript.text
        
        logger.info(f"Whisper transcription successful: {len(transcript_text)} characters")
        return transcript_text
    except Exception as e:
        error_msg = str(e)
        # Provide more helpful error message
        if "401" in error_msg or "invalid_api_key" in error_msg:
            logger.error("OpenAI API key is invalid. Please check your OPENAI_API_KEY in .env file.")
            raise ValueError(
                "Invalid OpenAI API key. Please verify:\n"
                "1. Key is correct in backend/.env file\n"
                "2. Key has no extra spaces or quotes\n"
                "3. Key is active at https://platform.openai.com/account/api-keys"
            )
        logger.error(f"OpenAI Whisper transcription failed: {e}")
        raise


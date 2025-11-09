"""Fallback TTS service using Google Text-to-Speech (gTTS)."""
import logging
import io
from gtts import gTTS

logger = logging.getLogger(__name__)


def synthesize_with_gtts(text: str, lang: str = "en") -> bytes:
    """
    Synthesize speech using gTTS and return MP3 bytes.

    Args:
        text: Text to synthesize.
        lang: Language code (default: English).

    Returns:
        MP3 audio bytes.
    """
    try:
        logger.info("Using gTTS fallback for speech synthesis (lang=%s)", lang)
        tts = gTTS(text=text, lang=lang)
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer.read()
    except Exception as exc:  # pragma: no cover - network IO
        logger.exception("gTTS synthesis failed: %s", exc)
        raise





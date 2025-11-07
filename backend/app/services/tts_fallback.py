"""Fallback TTS service using Eleven Labs directly when MCP is not available."""
import logging
import requests
from app.config import settings

logger = logging.getLogger(__name__)


def synthesize_with_elevenlabs(text: str, voice_id: str = None) -> bytes:
    """
    Synthesize speech using Eleven Labs API directly.
    
    Args:
        text: Text to synthesize
        voice_id: Voice ID to use (can be Eleven Labs voice ID or voice name)
                  Defaults to configured voice or Rachel
    
    Returns:
        Audio data as bytes (MP3)
    """
    if not settings.eleven_labs_api_key:
        raise ValueError("ELEVEN_LABS_API_KEY not configured. Cannot use Eleven Labs fallback.")
    
    # Voice ID mapping: frontend voice names to Eleven Labs voice IDs
    voice_id_map = {
        'rachel': '21m00Tcm4TlvDq8ikWAM',
        'domi': 'AZnzlk1XvdvUeBnXmlld',
        'bella': 'EXAVITQu4vr4xnSDxMaL',
        'antoni': 'ErXwobaYiN019lkyVLvD',
        'elli': 'MF3mGyEYCl7XYWbV9V6O',
        'josh': 'TxGEqnHWrfWFTfGW9XjX',
        'arnold': 'VR6AewLTigWG4xSOukaG',
        'adam': 'pNInz6obpgDQGcFmaJgB',
        'sam': 'yoZ06aMxZJJ28mfd3POQ',
        'default': '21m00Tcm4TlvDq8ikWAM',
    }
    
    # Convert voice name to Eleven Labs voice ID if needed
    if voice_id and voice_id in voice_id_map:
        voice_id = voice_id_map[voice_id]
    elif not voice_id:
        voice_id = settings.eleven_labs_voice_id or "21m00Tcm4TlvDq8ikWAM"  # Default to Rachel
    
    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "Accept": "audio/mpeg",
            "xi-api-key": settings.eleven_labs_api_key,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=30)
        
        # Check for authentication errors
        if response.status_code == 401:
            error_detail = response.text
            logger.error(f"Eleven Labs API authentication failed (401). Key may be invalid or expired.")
            raise ValueError(
                f"Eleven Labs API key is invalid or expired (401 Unauthorized). "
                f"Please verify your API key at https://elevenlabs.io/app/settings/api-keys "
                f"and update it in backend/.env file. Error: {error_detail[:200]}"
            )
        
        # Check for permission errors (481 or other status codes with permission issues)
        if response.status_code in [481, 403] or (response.status_code >= 400 and 'missing_permissions' in response.text):
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', {}).get('message', 'Missing permissions')
                if 'missing_permissions' in error_msg.lower() or 'permission' in error_msg.lower():
                    logger.error(f"Eleven Labs API permission error: {error_msg}")
                    raise ValueError(
                        f"Eleven Labs API key is missing required permissions. "
                        f"The key needs 'text_to_speech' permission. "
                        f"Please check your API key permissions at https://elevenlabs.io/app/settings/api-keys "
                        f"or create a new API key with text-to-speech access. "
                        f"Error: {error_msg}"
                    )
            except:
                pass
        
        response.raise_for_status()
        
        logger.info("Speech synthesis successful using Eleven Labs (fallback)")
        return response.content
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            logger.error("Eleven Labs API authentication failed (401)")
            raise ValueError(
                "Eleven Labs API key is invalid or expired. "
                "Please check your ELEVEN_LABS_API_KEY in backend/.env "
                "or get a new key from https://elevenlabs.io/app/settings/api-keys"
            )
        logger.error(f"Eleven Labs HTTP error: {e}")
        raise
    except Exception as e:
        logger.error(f"Eleven Labs synthesis failed: {e}")
        raise


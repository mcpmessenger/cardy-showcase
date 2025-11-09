"""
Quick STT/TTS smoke test against the running FastAPI backend.

Usage:
    # In one terminal start the backend (ensure OPENAI_API_KEY is set)
    uvicorn app.main:app --host 0.0.0.0 --port 8000

    # In another terminal run:
    python smoke_test.py
"""
import os
from io import BytesIO

import requests
from gtts import gTTS

TEST_TEXT = "The quick brown fox jumps over the lazy dog."
TMP_AUDIO = "test_audio.mp3"
API_BASE_URL = os.getenv("VOICE_API_BASE_URL", "http://localhost:8000/api")


def generate_audio() -> None:
    """Create a local MP3 file that mimics a user voice upload."""
    print(f"Generating test audio file: {TMP_AUDIO}")
    tts = gTTS(text=TEST_TEXT, lang="en")
    buffer = BytesIO()
    tts.write_to_fp(buffer)
    with open(TMP_AUDIO, "wb") as handle:
        handle.write(buffer.getvalue())
    print("Audio file generated successfully.")


def test_stt() -> None:
    """POST the audio file to the /api/stt/transcribe endpoint."""
    print("\n--- Testing STT Endpoint ---")
    with open(TMP_AUDIO, "rb") as handle:
        files = {"audio_file": (TMP_AUDIO, handle, "audio/mp3")}
        response = requests.post(f"{API_BASE_URL}/stt/transcribe", files=files, timeout=45)
    response.raise_for_status()
    payload = response.json()
    print(f"STT Status: {response.status_code}")
    print(f"STT Result: {payload}")

    transcribed = payload.get("text", "").strip().lower().replace(".", "")
    expected = TEST_TEXT.lower().replace(".", "")
    if expected in transcribed:
        print("STT Test: SUCCESS (transcription matched expectation)")
    else:
        raise AssertionError(
            f"STT Test failed: expected to contain '{expected}', got '{transcribed}'"
        )


def test_tts() -> None:
    """POST text to /api/tts/synthesize and verify gTTS fallback returns audio."""
    print("\n--- Testing TTS Endpoint ---")
    payload = {"text": "This is a test of the text-to-speech fallback."}
    response = requests.post(f"{API_BASE_URL}/tts/synthesize", json=payload, timeout=45)
    response.raise_for_status()
    body = response.json()
    print(f"TTS Status: {response.status_code}")
    audio_data = body.get("audio_data", "")
    if audio_data and len(audio_data) > 100:
        print(f"TTS Test: SUCCESS (received {len(audio_data)} base64 bytes)")
    else:
        raise AssertionError("TTS Test failed: response did not include audio_data.")


def cleanup() -> None:
    """Remove the temporary audio file."""
    if os.path.exists(TMP_AUDIO):
        os.remove(TMP_AUDIO)
        print(f"\nCleaned up {TMP_AUDIO}")


if __name__ == "__main__":
    try:
        generate_audio()
        test_stt()
        test_tts()
    finally:
        cleanup()


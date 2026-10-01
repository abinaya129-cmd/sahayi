"""Speech service: Google Cloud STT/TTS when creds exist; otherwise the
dashboard uses the browser's built-in SpeechRecognition/SpeechSynthesis
(zero cost, zero keys, works offline in Chrome/Edge).

The demo never depends on an external speech API - that is the whole point.
"""
import os

from ..config import settings

_client = None
_tts_client = None

if settings.GOOGLE_APPLICATION_CREDENTIALS and os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
    try:
        from google.cloud import speech_v1, texttospeech_v1
        _client = speech_v1.SpeechClient()
        _tts_client = texttospeech_v1.TextToSpeechClient()
    except Exception:
        _client = None
        _tts_client = None


def stt_available() -> bool:
    return _client is not None


def tts_available() -> bool:
    return _tts_client is not None


def status() -> dict:
    return {
        "stt": "google" if _client else "browser",
        "tts": "google" if _tts_client else "browser",
        "mode": "production" if (_client or _tts_client) else "demo",
    }


def speech_to_text(audio_bytes: bytes, language_code: str) -> dict:
    """Google STT. Returns {"text": ...} or {"error": ...}."""
    if _client is None:
        return {"error": "Google STT not configured (set GOOGLE_APPLICATION_CREDENTIALS)"}
    from google.cloud import speech_v1
    lang_map = {"hi": "hi-IN", "ta": "ta-IN", "te": "te-IN", "kn": "kn-IN", "ml": "ml-IN",
                "mr": "mr-IN", "gu": "gu-IN", "bn": "bn-IN", "pa": "pa-IN", "ur": "ur-IN",
                "or": "or-IN", "as": "as-IN"}
    audio = speech_v1.RecognitionAudio(content=audio_bytes)
    config = speech_v1.RecognitionConfig(
        language_code=lang_map.get(language_code, "hi-IN"),
        encoding=speech_v1.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        enable_automatic_punctuation=False,
    )
    resp = _client.recognize(config=config, audio=audio)
    text = " ".join(r.alternatives[0].transcript for r in resp.results if r.alternatives)
    return {"text": text}


def synthesize(text: str, language: str) -> bytes | None:
    """Google TTS mp3, or None when unavailable (browser TTS takes over)."""
    if _tts_client is None:
        return None
    from google.cloud import texttospeech_v1
    lang_map = {"hi": "hi-IN", "ta": "ta-IN", "te": "te-IN", "kn": "kn-IN", "ml": "ml-IN",
                "mr": "mr-IN", "gu": "gu-IN", "bn": "bn-IN", "pa": "pa-IN", "ur": "ur-IN",
                "or": "or-IN", "as": "as-IN"}
    resp = _tts_client.synthesize_speech(
        input=texttospeech_v1.SynthesisInput(text=text),
        voice=texttospeech_v1.VoiceSelectionParams(
            language_code=lang_map.get(language, "hi-IN"),
            ssml_gender=texttospeech_v1.SsmlVoiceGender.FEMALE),
        audio_config=texttospeech_v1.AudioConfig(
            audio_encoding=texttospeech_v1.AudioEncoding.MP3),
    )
    return resp.audio_content

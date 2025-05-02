import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs

load_dotenv()

client = ElevenLabs(
    api_key=os.environ.get("ELEVENLABS_KEY"),
)

def get_available_voices() -> list[dict]:
    """Возвращает список доступных голосов с именем и voice_id."""
    voices = client.voices.get_all().voices
    return [{"name": v.name, "id": v.voice_id} for v in voices]

def get_voice_id_by_name(name: str) -> str | None:
    """Находит voice_id по имени голоса."""
    voices = get_available_voices()
    for voice in voices:
        if voice["name"].lower() == name.lower():
            return voice["id"]
    return None

def generate_audio(text: str, voice_id: str, output_path: str = "audio.mp3") -> str:
    """Генерирует аудио и сохраняет его в файл."""
    audio = client.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    with open(output_path, "wb") as f:
        for chunk in audio:
            f.write(chunk)
    return output_path

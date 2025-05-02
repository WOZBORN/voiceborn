from gtts import gTTS

# Поддерживаемые языки с кратким описанием
SUPPORTED_LANGUAGES = {
    "ru": "Русский",
    "en": "Английский",
    "de": "Немецкий",
    "fr": "Французский",
    "es": "Испанский",
    "it": "Итальянский",
    "ja": "Японский",
    "ko": "Корейский",
    "zh": "Китайский",
}


def get_supported_languages() -> dict:
    """Возвращает словарь поддерживаемых языков."""
    return SUPPORTED_LANGUAGES


def generate_gtts_audio(text: str, lang: str = "ru", output_path: str = "gtts_audio.mp3") -> str:
    """Генерирует озвучку текста и сохраняет файл."""
    if lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Язык '{lang}' не поддерживается.")

    tts = gTTS(text=text, lang=lang)
    tts.save(output_path)
    return output_path


if __name__ == "__main__":
    text = "Я круто озвучиваю текст, потому что я - искусственный интеллект."
    lang = "ru"
    output_path = "gtts_audio.mp3"

    generate_gtts_audio(text, lang, output_path)
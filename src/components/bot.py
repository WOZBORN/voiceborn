import json
import os
from idlelib.iomenu import encoding

from dotenv import load_dotenv
import telebot
from telebot.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
                           CallbackQuery, Message, User)

from src.components.gtts_voice import get_supported_languages, generate_gtts_audio
from src.components.ai_voice import get_available_voices, generate_audio
import src.components.db_manager as db


load_dotenv()
db.init_db()

BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Текст для сообщений бота:
answers = json.load(open("src/answers.json", encoding="utf-8"))

# Память пользователя
user_last_message_id = {}
user_states = {}

# Структура состояния
# user_states[user_id] = {
#     "mode": "gtts" or "elevenlabs",
#     "lang": "ru",  # для gtts
#     "voice_id": "xxxx",  # для elevenlabs
# }

# --- Команды ---


def handle_exception(user: User, stage: str = "unknown"):
    import traceback

    # Получить owner_id из .env
    owner_id = os.environ.get("BOT_OWNER_TELEGRAM_ID")
    error_trace = traceback.format_exc()

    # Вывод в консоль
    print(f"[ERROR] На этапе: {stage}")
    print(f"[USER] {user.id} @{user.username or 'NoUsername'}")
    print(error_trace)

    # Сообщение для владельца
    if owner_id:
        try:
            bot.send_message(
                int(owner_id),
                f"❗ Ошибка в боте\n"
                f"👤 Пользователь: {user.id} @{user.username or 'Без ника'}\n"
                f"📍 Этап: {stage}\n"
            )
        except Exception as owner_err:
            print("[ERROR] Не удалось отправить сообщение владельцу:", owner_err)


@bot.message_handler(commands=['start'])
def start_handler(message: Message):
    user_id = message.from_user.id
    db.ensure_user_exists(user_id)

    user_states[user_id] = {}  # Сбросить состояния

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎤 gTTS", callback_data="mode_gtts"))
    markup.add(InlineKeyboardButton("🎙 ElevenLabs", callback_data="mode_elevenlabs"))

    sent_message = bot.send_message(message.chat.id, answers["start"], reply_markup=markup)
    user_last_message_id[user_id] = sent_message.message_id

@bot.message_handler(commands=['info'])
def info_handler(message: Message):
    bot.send_message(message.chat.id, answers["info"])

# --- Обработка нажатий кнопок ---

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call: CallbackQuery):
    user_id = call.from_user.id

    if call.data:
        chat = call.message.chat.id
        # Удалить последнее сообщение с кнопками
        last_message_id = user_last_message_id.get(user_id)
        if last_message_id:
            try:
                bot.delete_message(chat_id=chat, message_id=last_message_id)
            except Exception as e:
                print(f"Error deleting message: {e}")


    if call.data == "mode_gtts":
        user_states[user_id] = {"mode": "gtts"}
        choose_gtts_language(call.message, user_id)

    elif call.data == "mode_elevenlabs":
        user_states[user_id] = {"mode": "elevenlabs"}
        choose_elevenlabs_voice(call, user_id)

# --- Выбор языка для gTTS ---

def choose_gtts_language(message: Message, user_id: int):
    langs = get_supported_languages()
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for code, name in langs.items():
        markup.add(KeyboardButton(f"{code} — {name}"))

    bot.send_message(message.chat.id, "Выберите язык для озвучки:", reply_markup=markup)

# --- Выбор голоса для ElevenLabs ---

def choose_elevenlabs_voice(call: CallbackQuery, user_id: int):
    try:
        voices = get_available_voices()
    except Exception:
        handle_exception(call.from_user, stage="get_available_voices")
        bot.send_message(call.message.chat.id, answers["elevenlabs_error"])
        return
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for voice in voices:
        markup.add(KeyboardButton(voice["name"]))

    allowed, used, total = db.has_enough_limit(user_id)
    limit_ended = " (Лимит исчерпан!)" if not allowed else ""
    bot.send_message(
        call.message.chat.id,
        f"Использовано {used}/{total}{limit_ended}\nВыберите голос для озвучки:",
        reply_markup=markup
    )

# --- Обработка текстовых сообщений ---

@bot.message_handler(func=lambda message: True)
def text_handler(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if user_id not in user_states:
        bot.send_message(message.chat.id, "Сначала нажмите /start.")
        return

    user_data = user_states[user_id]

    if user_data.get("mode") == "gtts":
        if "lang" not in user_data:
            # Пользователь выбирает язык
            code = text.split("—")[0].strip()
            langs = get_supported_languages()
            if code in langs:
                user_states[user_id]["lang"] = code
                bot.send_message(message.chat.id, f"Выбран язык: {langs[code]}.\nТеперь отправьте текст для озвучки.", reply_markup=ReplyKeyboardRemove())
            else:
                bot.send_message(message.chat.id, "Неверный язык. Выберите язык из списка.")
        else:
            # Генерация аудио
            lang = user_data["lang"]
            file_path = generate_gtts_audio(text, lang=lang, output_path=f"{user_id}_gtts.mp3")
            with open(file_path, "rb") as f:
                bot.send_audio(message.chat.id, f)
            os.remove(file_path)

    elif user_data.get("mode") == "elevenlabs":
        if "voice_id" not in user_data:
            # Пользователь выбирает голос
            voice_name = text.strip()
            voices = get_available_voices()
            voice_id = None
            for voice in voices:
                if voice["name"].lower() == voice_name.lower():
                    voice_id = voice["id"]
                    break
            if voice_id:
                user_states[user_id]["voice_id"] = voice_id
                bot.send_message(message.chat.id, f"Выбран голос: {voice_name}.\nТеперь отправьте текст для озвучки.", reply_markup=ReplyKeyboardRemove())
            else:
                bot.send_message(message.chat.id, "Неверный голос. Выберите голос из списка.")
        else:
            # Генерация аудио
            try:
                allowed, used, total = db.has_enough_limit(user_id, text)
                if not allowed:
                    bot.send_message(message.chat.id, f"❌ Лимит исчерпан.\n{used}/{total} символов использовано.\nДней до обнуления л\nПока воспользуйся gTTS /start")
                    return
                voice_id = user_data["voice_id"]
                file_path = generate_audio(text, voice_id=voice_id, output_path=f"{user_id}_elevenlabs.mp3")
                if os.path.exists(file_path):
                    db.increment_limit_usage(user_id, len(text))
                    bot.send_message(message.chat.id, f"✅ Генерация прошла успешно! Использовано: {used+len(text)}/{total}")
                    with open(file_path, "rb") as f:
                        bot.send_audio(message.chat.id, f)
                    os.remove(file_path)
            except:
                bot.send_message(message.chat.id, answers["error"])

    else:
        bot.send_message(message.chat.id, "Сначала выберите режим генерации через /start.")

# --- Запуск бота ---
def start_bot():
    bot.polling(none_stop=True)

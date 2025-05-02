# VOICEBORN
Телеграм бот для создвания озвучек.

Задействованные сервсиы:
* ElevenLabs - ИИ озвучка (с лимитами - базово 1000)
* gTTS - Google Text To Speech (без ИИ)

Сам бот:
* @voiceborn_bot
* https://t.me/voiceborn_bot

### Как запускать
1. Клонируем проект:
```bash
git clone https://github.com/wozborn/voiceborn.git
```
2. Создаем виртуальное окружение:
```bash
python3 -m venv venv
```
3. Активируем виртуальное окружение:

Для Win:
```bash
venv/Scripts/activate
```
Для Linux/Mac:
```bash
source venv/bin/activate
```
4. Устанавливаем зависимости:
```bash
pip install -r requirements.txt
```
5. Создаем файл `.env` с переменными окружения:
```bash
BOT_TOKEN="токен бота от @BotFather в кавычках"
ELEVENLABS_KEY="ключ от elevenlabs в кавычках"
BOT_OWNER_TELEGRAM_ID=<ваш телеграм id не в скобочках>
```
6. Запускаем бота:
```bash
python main.py
```


# Telegram AI Assistant Bot

Короткий учебный проект: Telegram-бот с подключением OpenAI и GigaChat.

## Быстрый старт

1. Установите зависимости:
   - `pip install -r requirements.txt`
2. Заполните файл `.env` своими ключами.
3. Запустите нужный скрипт:
   - OpenAI Assistant: `python main_openai_assistant.py`
   - OpenAI Responses: `python main_openai_responses.py`
   - GigaChat: `python main_gigachat.py`

## Что важно в .env

- `TELEGRAM_TOKEN` — токен бота из BotFather  
- `OPENAI_API_KEY` — ключ OpenAI  
- `ASSISTANT_ID` — ID ассистента OpenAI  
- `GIGACHAT_CREDENTIALS` — Authorization Key или base64(ClientID:ClientSecret)  
- `GIGACHAT_SCOPE` — обычно `GIGACHAT_API_PERS`

## Частая ошибка

Если видите `409 Conflict`, значит бот уже запущен где-то еще.  
Оставьте только один активный запуск.

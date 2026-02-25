import logging
from pathlib import Path
from typing import List

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from langchain_core.messages import HumanMessage

from src import GIGACHAT_MODEL, TELEGRAM_TOKEN
from src.observability import finish_generation_observation, start_generation_observation
from src.services import get_gigachat_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
MAX_TELEGRAM_TEXT_LEN = 3900

giga = get_gigachat_client()

CONTEXT_FILE = Path("data/context.pdf")
FILE_ID = None

if CONTEXT_FILE.exists():
    with CONTEXT_FILE.open("rb") as file_obj:
        uploaded_file = giga.upload_file(file_obj)
        FILE_ID = uploaded_file.id_
        logger.info("Загружен контекстный файл с id=%s", FILE_ID)

SYSTEM_PROMPT = """
Роль модели: маркетолог и контент-редактор маркетплейсов (Ozon/Wildberries).
Сделай карточку товара по запросу пользователя.
Нужны разделы:
- Название товара
- Краткое описание
- Полное описание
- Преимущества
- Характеристики
- SEO-ключевые слова
"""


def split_text_for_telegram(text: str, chunk_size: int = MAX_TELEGRAM_TEXT_LEN) -> List[str]:
    normalized_text = text or "Нет ответа от GigaChat."
    return [normalized_text[i : i + chunk_size] for i in range(0, len(normalized_text), chunk_size)]


async def send_response_safely(update: Update, status_msg, response_text: str) -> None:
    parts = split_text_for_telegram(response_text)
    if not parts:
        await status_msg.edit_text("Нет ответа от GigaChat.")
        return

    try:
        await status_msg.edit_text(parts[0])
    except TelegramError:
        # Если редактирование не удалось, отправляем новым сообщением.
        await update.message.reply_text(parts[0])

    for part in parts[1:]:
        await update.message.reply_text(part)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я бот-помощник через GigaChat.\n"
        "Отправь сообщение, и я создам карточку товара."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    user_id = str(update.message.from_user.id)
    status_msg = await update.message.reply_text("Обрабатываю запрос через GigaChat...")
    observation = start_generation_observation(
        name="telegram-gigachat",
        user_id=user_id,
        model=GIGACHAT_MODEL,
        input_data=user_message,
        metadata={"channel": "telegram", "provider": "gigachat"},
    )

    try:
        if FILE_ID:
            user_payload = HumanMessage(
                content=user_message,
                additional_kwargs={"attachments": [FILE_ID]},
            )
        else:
            user_payload = HumanMessage(content=user_message)

        messages = [("system", SYSTEM_PROMPT), user_payload]
        response = giga.invoke(messages, request_kwargs={"timeout": 180})
        response_text = response.content if response else "Нет ответа от GigaChat."
        finish_generation_observation(observation, output_data=response_text)
        await send_response_safely(update, status_msg, response_text)
    except Exception as error:
        logger.exception("Ошибка GigaChat: %s", error)
        finish_generation_observation(observation, error=error)
        await status_msg.edit_text("Ошибка при обработке запроса. Попробуйте позже.")


def main() -> None:
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN не найден в .env")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот GigaChat запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()

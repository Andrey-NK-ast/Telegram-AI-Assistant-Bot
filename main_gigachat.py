import logging
from pathlib import Path

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from langchain_core.messages import HumanMessage

from src import TELEGRAM_TOKEN
from src.services import get_gigachat_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я бот-помощник через GigaChat.\n"
        "Отправь сообщение, и я создам карточку товара."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    status_msg = await update.message.reply_text("Обрабатываю запрос через GigaChat...")

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
        await status_msg.edit_text(response_text)
    except Exception as error:
        logger.error("Ошибка GigaChat: %s", error)
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

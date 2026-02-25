import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from src import TELEGRAM_TOKEN
from src.services import get_openai_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = get_openai_client()

SYSTEM_PROMPT = """
Роль модели: маркетолог и контент-редактор маркетплейсов (Ozon/Wildberries).
Задача: создать карточку товара для маркетплейса по запросу пользователя.
Карточка должна включать:
- Название товара
- Краткое описание (1-2 предложения)
- Полное описание (5-7 предложений)
- Преимущества (список)
- Характеристики (список параметров)
- SEO-ключевые слова (через запятую)
Стиль: информативный и продающий, до 500 слов.
"""


def get_openai_response(user_input: str) -> str:
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
    )
    return response.output_text if response.output_text else "Нет ответа от модели."


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я бот-помощник через OpenAI Responses API.\n"
        "Отправь сообщение, и я помогу сделать карточку товара."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    status_msg = await update.message.reply_text("Обрабатываю запрос...")
    try:
        response_text = get_openai_response(user_message)
        await status_msg.edit_text(response_text)
    except Exception as error:
        logger.error("Ошибка OpenAI Responses API: %s", error)
        await status_msg.edit_text("Ошибка при обработке запроса. Попробуйте позже.")


def main() -> None:
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN не найден в .env")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот OpenAI Responses запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()

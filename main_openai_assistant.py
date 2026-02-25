import asyncio
import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

from src import ASSISTANT_ID, TELEGRAM_TOKEN
from src.observability import finish_generation_observation, start_generation_observation
from src.services import get_openai_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = get_openai_client()
user_threads = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я бот-помощник через OpenAI Assistant.\n"
        "Отправь сообщение, и я помогу сделать карточку товара."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    user_id = update.message.from_user.id
    status_msg = await update.message.reply_text("Обрабатываю запрос...")
    observation = start_generation_observation(
        name="telegram-openai-assistant",
        user_id=str(user_id),
        model="openai-assistant",
        input_data=user_message,
        metadata={"channel": "telegram", "assistant_id": ASSISTANT_ID},
    )

    try:
        if user_id in user_threads:
            thread_id = user_threads[user_id]
        else:
            thread = client.beta.threads.create()
            thread_id = thread.id
            user_threads[user_id] = thread_id

        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message,
        )

        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID,
        )

        while run.status in {"queued", "in_progress"}:
            await asyncio.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        messages = client.beta.threads.messages.list(thread_id=thread_id)
        response_texts = [
            msg.content[0].text.value
            for msg in reversed(messages.data)
            if msg.role == "assistant" and msg.content
        ]
        response = "\n".join(response_texts) if response_texts else "Нет ответа от ассистента."
        finish_generation_observation(observation, output_data=response)
        await status_msg.edit_text(response)
    except Exception as error:
        logger.error("Ошибка OpenAI Assistant: %s", error)
        finish_generation_observation(observation, error=error)
        await status_msg.edit_text("Ошибка при обработке запроса. Попробуйте позже.")


def main() -> None:
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN не найден в .env")
    if not ASSISTANT_ID:
        raise ValueError("ASSISTANT_ID не найден в .env")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Бот OpenAI Assistant запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()

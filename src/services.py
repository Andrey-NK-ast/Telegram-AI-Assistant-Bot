from openai import OpenAI

from src.config import get_settings

try:
    from langchain_gigachat.chat_models import GigaChat
except Exception:  # pragma: no cover
    GigaChat = None


def get_openai_client() -> OpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY не найден в .env")
    return OpenAI(api_key=settings.openai_api_key)


def get_gigachat_client():
    if GigaChat is None:
        raise ImportError("Пакет langchain-gigachat не установлен.")

    settings = get_settings()
    if not settings.gigachat_credentials:
        raise ValueError("GIGACHAT_CREDENTIALS не найден в .env")

    return GigaChat(
        model=settings.gigachat_model,
        credentials=settings.gigachat_credentials,
        scope=settings.gigachat_scope,
        verify_ssl_certs=settings.gigachat_verify_ssl,
        profanity_check=True,
    )

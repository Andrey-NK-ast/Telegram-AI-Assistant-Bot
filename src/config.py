import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv(override=True)


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    assistant_id: str
    telegram_token: str
    gigachat_credentials: str
    gigachat_model: str
    gigachat_scope: str
    gigachat_verify_ssl: bool
    langfuse_secret_key: str
    langfuse_public_key: str
    langfuse_host: str


def _to_bool(raw_value: Optional[str], default: bool = False) -> bool:
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


def get_settings() -> Settings:
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        assistant_id=os.getenv("ASSISTANT_ID", ""),
        telegram_token=os.getenv("TELEGRAM_TOKEN", ""),
        gigachat_credentials=os.getenv("GIGACHAT_CREDENTIALS", ""),
        gigachat_model=os.getenv("GIGACHAT_MODEL", "GigaChat-Pro"),
        gigachat_scope=os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS"),
        gigachat_verify_ssl=_to_bool(os.getenv("GIGACHAT_VERIFY_SSL"), default=False),
        langfuse_secret_key=os.getenv("LANGFUSE_SECRET_KEY", ""),
        langfuse_public_key=os.getenv("LANGFUSE_PUBLIC_KEY", ""),
        langfuse_host=os.getenv("LANGFUSE_HOST", ""),
    )

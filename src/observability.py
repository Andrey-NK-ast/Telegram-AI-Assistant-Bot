import logging
from typing import Any, Optional

from src.config import get_settings

try:
    from langfuse import Langfuse
except Exception:  # pragma: no cover
    Langfuse = None

logger = logging.getLogger(__name__)

_langfuse_client: Optional[Any] = None
_langfuse_initialized = False


def get_langfuse_client() -> Optional[Any]:
    global _langfuse_client
    global _langfuse_initialized

    if _langfuse_initialized:
        return _langfuse_client

    _langfuse_initialized = True

    if Langfuse is None:
        return None

    settings = get_settings()
    if not (settings.langfuse_public_key and settings.langfuse_secret_key and settings.langfuse_host):
        return None

    try:
        _langfuse_client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )
    except Exception as error:  # pragma: no cover
        logger.error("Ошибка инициализации Langfuse: %s", error)
        _langfuse_client = None

    return _langfuse_client


def start_generation_observation(
    name: str,
    user_id: str,
    model: str,
    input_data: Any,
    metadata: Optional[dict] = None,
) -> Optional[Any]:
    client = get_langfuse_client()
    if client is None:
        return None

    try:
        observation = client.start_observation(
            name=name,
            as_type="generation",
            input=input_data,
            model=model,
            metadata=metadata or {},
        )
        observation.update_trace(name=name, user_id=user_id)
        return observation
    except Exception as error:  # pragma: no cover
        logger.error("Ошибка старта наблюдения Langfuse: %s", error)
        return None


def finish_generation_observation(
    observation: Optional[Any],
    output_data: Optional[Any] = None,
    error: Optional[Exception] = None,
) -> None:
    if observation is None:
        return

    try:
        if error is None:
            observation.update(output=output_data)
        else:
            observation.update(
                output=output_data,
                level="ERROR",
                status_message=str(error),
                metadata={"error_type": type(error).__name__},
            )
        observation.end()

        client = get_langfuse_client()
        if client is not None:
            client.flush()
    except Exception as track_error:  # pragma: no cover
        logger.error("Ошибка отправки данных в Langfuse: %s", track_error)

from src.config import get_settings

_settings = get_settings()

OPENAI_API_KEY = _settings.openai_api_key
ASSISTANT_ID = _settings.assistant_id
TELEGRAM_TOKEN = _settings.telegram_token
GIGACHAT_CREDENTIALS = _settings.gigachat_credentials
GIGACHAT_MODEL = _settings.gigachat_model
GIGACHAT_SCOPE = _settings.gigachat_scope
GIGACHAT_VERIFY_SSL = _settings.gigachat_verify_ssl
LANGFUSE_SECRET_KEY = _settings.langfuse_secret_key
LANGFUSE_PUBLIC_KEY = _settings.langfuse_public_key
LANGFUSE_HOST = _settings.langfuse_host

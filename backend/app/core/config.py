from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    NHORA_API_URL: str = "http://localhost:8000"
    CORS_ORIGINS: str = "http://localhost:3300,http://127.0.0.1:3300"
    CHATWOOT_BASE_URL: str
    CHATWOOT_ACCOUNT_ID: int = 1
    CHATWOOT_API_TOKEN: str
    CHATWOOT_INBOX_LEADS_ID: int = 1
    CHATWOOT_INBOX_CAMPANHAS_INTERNAS_ID: int = 2
    CHATWOOT_INBOX_SUPORTE_ID: int = 3
    CHATWOOT_INBOX_TRANSACIONAL_ID: int = 4
    REQUEST_TIMEOUT_SECONDS: int = 30
    N8N_ACTIVE_SEND_URL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

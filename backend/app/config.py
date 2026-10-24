from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_PAGE_SIZE = 25
MAX_PAGE_SIZE = 100
DEFAULT_CORS_ORIGINS = ["http://localhost:5173"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="STAFFSENSE_")

    app_name: str = "StaffSense"
    database_url: str = "sqlite:///./staffsense.db"
    cors_origins: list[str] = DEFAULT_CORS_ORIGINS
    default_page_size: int = DEFAULT_PAGE_SIZE
    max_page_size: int = MAX_PAGE_SIZE


settings = Settings()

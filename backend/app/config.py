from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="STAFFSENSE_")

    app_name: str = "StaffSense"
    database_url: str = "sqlite:///./staffsense.db"


settings = Settings()

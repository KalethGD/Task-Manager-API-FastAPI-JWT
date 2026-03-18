from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    #Database settings
    database_url: str

    #jwt
    secret_key: str = 'tu-super-secret-key-cambiar-en-produccion'
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    model_config = SettingsConfigDict(
        env_file='.env',
        case_sensitive=False
    )

@lru_cache()
def get_settings():
    return Settings()
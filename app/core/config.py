from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str
    DEBUG: bool
    DATABASE_URL: str
    SYNC_DATABASE_URL: str
    REDIS_URL: str
    UPLOAD_DIR: str
    MAX_UPLOAD_SIZE_MB: int
    HF_TOKEN: str
    WHISPER_MODEL_SIZE: str = "base"
    OPENAI_API_KEY: str
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-4o-mini"
    CHUNK_OVERLAP_WORDS: int = 10

    # auth — keeping here even though we implement later
    SECRET_KEY: str = "changeme"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
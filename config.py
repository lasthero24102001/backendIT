from pydantic_settings import BaseSettings,SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL:str
    REDIS_URL: Optional[str]=None
    SECRET_KEY:str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES:int=30
    REFRESH_TOKEN_EXPIRE_DAYS:int=30
    model_config = SettingsConfigDict(env_file='.env',env_file_encoding='utf-8',extra='ignore')

settings = Settings()
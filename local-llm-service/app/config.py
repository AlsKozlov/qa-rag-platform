from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MODEL_NAME: str
    HF_TOKEN: str
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
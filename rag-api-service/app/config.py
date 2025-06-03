from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    VEC_URI: str
    VEC_DIM: int
    MAX_TOKENS: str
    COLLECTION_NAME: str
    ENCODER_URL: str
    LOCAL_LMM_SERVICE_API: str
    RAG_SYSTEM: str
    SUMM_SYSTEM: str 
    QUESTION_MESSAGE: str
    QUESTION_DATABASE_MESSAGE: str
    SUMM_MESSAGE: str
    YANDEX_API_KEY: str
    GIGACHAT_MODEL_URI: str
    MODEL_URI: str
    MODEL_URI_32k: str
    COMP_URL: str
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASS: str
    DATABASE_NAME:str
    REDIS_HOST: str
    REDIS_PORT: int
    ADD_HISTORY_TOPIC_NAME: str
    UPDATE_HISTORY_TOPIC_NAME: str

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASS}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
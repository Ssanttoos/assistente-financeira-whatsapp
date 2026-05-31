"""
Configurações da aplicação
Lê variáveis de ambiente do arquivo .env
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Firebase
    firebase_credentials_path: str = "config/firebase-credentials.json"
    firebase_project_id: str = ""

    # Evolution API
    evolution_api_url: str = ""
    evolution_api_key: str = ""
    evolution_instance_name: str = ""

    # Aplicação
    app_env: str = "development"
    log_level: str = "INFO"
    webhook_secret: str = ""

    # OpenAI (opcional - para NLP avançado)
    openai_api_key: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

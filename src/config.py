import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "Chatbot API")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    VERSION: str = os.getenv("VERSION", "0.1.0")
    LOG_LEVEL: str = (
        "DEBUG"
        if os.getenv("ENVIRONMENT") == "test"
        else os.getenv("LOG_LEVEL", "INFO")
    )
    API_KEY: str = os.getenv("API_KEY", "your-secret-api-key")
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(
        ","
    )
    ALLOWED_HOSTS: list = os.getenv(
        "ALLOWED_HOSTS", "localhost,127.0.0.1,host.docker.internal"
    ).split(",")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")


settings = Settings()

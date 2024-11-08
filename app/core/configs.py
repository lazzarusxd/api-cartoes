from os import environ

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class Settings(BaseModel):

    API_V1: str = "/api/v1"
    DB_URL: str = environ.get("DB_URL")
    JWT_SECRET: str = environ.get("JWT_SECRET")
    ALGORITHM: str = environ.get("ALGORITHM")
    TOKEN_EXPIRATION_MINUTES: int = int(environ.get("TOKEN_EXPIRATION_MINUTES"))

    class Config:
        case_sensitive = True


settings: Settings = Settings()

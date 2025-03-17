import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()


class Settings(BaseSettings):
    """
    Pydantic settings model to load and validate environment variables.

    This class defines settings that are loaded from environment variables:
    - SECRET_KEY: The secret key used for cryptographic operations.
    - ALGORITHM: The algorithm used for JWT token encoding/decoding.
    - ACCESS_TOKEN_EXPIRE_MINUTES: The expiration time of access tokens in minutes.
    - DATABASE_URL: The URL for the asynchronous database connection.
    - SYNC_DATABASE_URL: The URL for the synchronous database connection (if needed).

    This class inherits from `BaseSettings` provided by `pydantic_settings` to load
    environment variables and perform validation.
    """
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    SYNC_DATABASE_URL: str = os.getenv("SYNC_DATABASE_URL")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    FAISS_INDEX_DIR: str = os.getenv("FAISS_INDEX_DIR")


# Instantiate settings based on the loaded environment variables
settings = Settings()

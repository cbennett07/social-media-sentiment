from pydantic_settings import BaseSettings


class APISettings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/sentiment"

    # API settings
    default_page_size: int = 20
    max_page_size: int = 100

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"

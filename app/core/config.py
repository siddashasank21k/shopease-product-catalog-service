from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "ShopEase Product Catalog Service"
    ENVIRONMENT: str = "development"
    PORT: int = 8003
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    LOW_STOCK_THRESHOLD: int = 10

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

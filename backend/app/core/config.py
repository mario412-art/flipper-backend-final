from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Flipper Calculator API"
    ENVIRONMENT: str = "development"

    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_JWT_SECRET: str

    GEMINI_API_KEY: str

    EBAY_CLIENT_ID: str
    EBAY_CLIENT_SECRET: str
    EBAY_ACCOUNT_DELETION_VERIFICATION_TOKEN: str
    EBAY_ACCOUNT_DELETION_ENDPOINT: str

    MARKET_DATA_PROVIDER: str = "mock"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()

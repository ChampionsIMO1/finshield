from pydantic_settings import BaseSettings
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str
    plaid_client_id: str = ""
    plaid_secret: str = ""
    plaid_env: str = "sandbox"
    openai_api_key: str = ""
    jwt_secret: str = "changeme"
    supabase_service_key: str = ""

    class Config:
        env_file = str(ROOT_DIR / ".env")

settings = Settings()
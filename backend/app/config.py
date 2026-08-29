from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://spaceevents:spaceevents@localhost/spaceevents"
    REDIS_URL: str = "redis://localhost:6379/0"
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    NASA_API_KEY: str = "DEMO_KEY"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    VAPID_PRIVATE_KEY: str = ""
    VAPID_PUBLIC_KEY: str = ""
    VAPID_CLAIM_EMAIL: str = "admin@lookupapp.app"
    # Firebase — paste the service account JSON as a single-line string
    FIREBASE_CREDENTIALS_JSON: str = ""
    # White-label admin — set a long random string; required to use /api/admin/* endpoints
    ADMIN_KEY: str = ""

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

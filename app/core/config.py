from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Math Solver API"
    jwt_secret: str = "CHANGE_ME"
    jwt_algorithm: str = "HS256"
    mongodb_url: str = "mongodb://localhost:27017/math-solver"
    redis_url: str = "redis://localhost:6379/0"
    access_token_expire_minutes: int = 15
    refresh_token_expire_minutes: int = 60 * 24 * 7
    google_client_id: str | None = None
    redirect_url: str = "http://localhost:5050"

settings = Settings()

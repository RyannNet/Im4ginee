import os
from functools import lru_cache


class Settings:
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    # Database
    ENV: str = os.getenv("ENV", "dev")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")

    # Storage
    STORAGE_DIR: str = os.getenv("STORAGE_DIR", "/workspace/backend/storage")
    IMAGES_DIR_NAME: str = "images"
    VIDEOS_DIR_NAME: str = "videos"
    UPSCALES_DIR_NAME: str = "upscales"

    # Celery / Redis
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

    # Models
    MODELS_DIR: str = os.getenv("MODELS_DIR", "/workspace/backend/models")
    SD_MODEL_ID: str = os.getenv("SD_MODEL_ID", "runwayml/stable-diffusion-v1-5")
    SD_INPAINT_MODEL_ID: str = os.getenv("SD_INPAINT_MODEL_ID", "stabilityai/stable-diffusion-2-inpainting")
    REAL_ESRGAN_MODEL: str = os.getenv("REAL_ESRGAN_MODEL", "x4plus")
    STABLE_VIDEO_MODEL_ID: str = os.getenv("STABLE_VIDEO_MODEL_ID", "stabilityai/stable-video-diffusion-img2vid-xt")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()

    # Ensure storage dirs exist
    for sub in (
        settings.IMAGES_DIR_NAME,
        settings.VIDEOS_DIR_NAME,
        settings.UPSCALES_DIR_NAME,
    ):
        path = os.path.join(settings.STORAGE_DIR, sub)
        os.makedirs(path, exist_ok=True)

    return settings

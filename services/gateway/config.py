import os
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)
GATEWAY_HOST = os.getenv("GATEWAY_HOST", "0.0.0.0")
GATEWAY_PORT = int(os.getenv("GATEWAY_PORT", "5000"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////data/app.db")
MODELS_DIR = os.getenv("MODELS_DIR", "/data/models")
os.makedirs(MODELS_DIR, exist_ok=True)

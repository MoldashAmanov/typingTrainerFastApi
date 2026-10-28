from pathlib import Path
import secrets

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = f"sqlite:///{BASE_DIR / 'typing_trainer.db'}"

SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

MIN_TEXT_LENGTH = 40
MAX_TEXT_LENGTH = 10000
DEFAULT_TEXT_LIMIT = 80

SUPPORTED_LANGUAGES = {'en', 'ru'}

UPLOAD_DIR = BASE_DIR / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)

MAX_UPLOAD_SIZE_BYTES = 2 * 1024 * 1024
ALLOWED_UPLOAD_EXTENSIONS = {".txt", ".md"}

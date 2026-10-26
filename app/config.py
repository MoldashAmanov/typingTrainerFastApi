from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_URL = f"sqlite:///{BASE_DIR / 'typing_trainer.db'}"

MIN_TEXT_LENGTH = 40
MAX_TEXT_LENGTH = 10000
DEFAULT_TEXT_LIMIT = 80

SUPPORTED_LANGUAGES = {'en', 'ru'}

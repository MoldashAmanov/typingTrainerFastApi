from datetime import datetime, timezone
from enum import Enum
from sqlmodel import Field, SQLModel

class Language(str, Enum):
    english = 'en'
    russian = 'ru'


class Text(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    language: Language = Field(index=True)
    content: str
    difficulty: int = Field(default=1, ge=1, le=5)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class TypingSession(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    text_id: int = Field(foreign_key='text.id', index=True)
    language: Language = Field(index=True)

    typed_text: str
    duration_seconds: float = Field(gt=0)
    wpm: float
    accuracy: float
    correct_chars: int
    incorrect_chars: int
    missed_chars: int
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    
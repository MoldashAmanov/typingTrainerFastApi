from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from app.models import Language


class TextCreate(BaseModel):
    language: Language
    content: str = Field(min_length=40, max_length=5000)
    difficulty: int = Field(default=1, ge=1, le=5)


class TextRead(BaseModel):
    id: int
    language: Language
    content: str
    difficulty: int
    created_at: datetime


class PracticeTextRead(BaseModel):
    session_seed: str
    text_id: int
    language: Language
    content: str
    difficulty: int


class SessionCreate(BaseModel):
    text_id: int
    typed_text: str
    duration_seconds: float = Field(gt=0, le=5000)


class SessionRead(BaseModel):
    id: int
    text_id: int
    language: Language
    typed_text: str
    duration_seconds: float
    wpm: float
    accuracy: float
    correct_chars: int
    incorrect_chars: int
    missed_chars: int
    created_at: datetime


class StatsRead(BaseModel):
    language: Language
    total_sessions: int
    average_wpm: float
    best_wpm: float
    average_accuracy: float
    total_practice_seconds: float


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TextImportResult(BaseModel):
    created_text: int
    skipped_lines: int
    language: Language
    source_filename: str
    
    
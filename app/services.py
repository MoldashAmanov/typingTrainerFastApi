import secrets
from dataclasses import dataclass
from sqlmodel import Session, select
from app.models import Language, Text, TypingSession

@dataclass(frozen=True)
class TypingResult:
    wpm: float
    accuracy: float
    correct_chars: int
    incorrect_chars: int
    missed_chars: int


def compare_texts(original: str, typed: str) -> TypingSession:
    original = original.strip()
    typed = typed.strip()

    correct = 0
    incorrect = 0

    for index, expected_char in enumerate(original):
        if index >= len(typed):
            break

        if typed[index] == expected_char:
            correct += 1
        else:
            incorrect += 1

    missed = max(len(original) - len(typed), 0)
    total = correct + incorrect + missed

    accuracy = round((correct / total) * 100, 2) if total else 0.0

    words = len(original.split())
    minutes = len(typed) / 5 / 60

    wpm = round(words / minutes, 2) if minutes > 0 else 0.0

    return TypingResult(
        wpm=wpm,
        accuracy=accuracy,
        correct_chars=correct,
        incorrect_chars=incorrect,
        missed_chars=missed,
    )


def get_random_text(
        session: Session,
        language: Language,
        difficulty: int | None = None
) -> Text | None:
    statement = select(Text).where(Text.language == language)
    if difficulty is not None:
        statement = statement.where(Text.difficulty == difficulty)

    texts = session.exec(statement).all()

    if not texts:
        return None

    return secrets.choice(texts)


def get_language_stats(
        session: Session,
        language: Language
) -> dict:
    sessions = session.exec(
        select(TypingSession).where(TypingSession.language == language)
        ).all()

    if not sessions:
        return {
            'language': language,
            'total_sessions': 0,
            'average_wpm': 0.0,
            'best_wpm': 0.0,
            'average_accuracy': 0.0,
            'total_practice_seconds': 0.0,
        }

    return {
        'language': language,
        'total_sessions': 0,
        'average_wpm': round(sum(s.wpm for s in sessions) / len(sessions), 2),
        'best_wpm': round(max(s.wpm for s in sessions), 2),
        'average_accuracy': round(sum(s.accuracy for s in sessions) / len(sessions), 2),
        'total_practice_seconds': round(sum(s.duration_seconds for s in sessions), 2),
    }
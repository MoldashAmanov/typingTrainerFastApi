from dataclasses import dataclass
from app.config import MAX_TEXT_LENGTH, MIN_TEXT_LENGTH


@dataclass(frozen=True)
class ParsedTextFile:
    texts: list[str]
    skipped_lines: int


def parse_text_file(content: str) -> ParsedTextFile:
    texts: list[str] = []
    skipped: int = 0

    for raw_line in content.splitlines():
        line = raw_line.strip()

        if not line:
            continue

        if len(line) < MIN_TEXT_LENGTH or len(line) > MAX_TEXT_LENGTH:
            skipped += 1
            continue

        texts.append(line)

    return ParsedTextFile(texts=texts, skipped_lines=skipped)
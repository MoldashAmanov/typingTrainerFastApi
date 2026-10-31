import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel
from alembic import context

# --- 1. Корень проекта в sys.path, чтобы импортировать app.* ---
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# --- 2. Импортируем модели ДО target_metadata ---
# Это регистрирует User, Text, TypingSession в SQLModel.metadata
from app import models  # noqa: F401
from app.config import DATABASE_URL

# --- 3. Конфиг Alembic ---
config = context.config

# Берём URL из app.config, а не из alembic.ini — единый источник правды
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- 4. Метаданные — ПОСЛЕ импорта моделей ---
target_metadata = SQLModel.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
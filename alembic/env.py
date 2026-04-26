from logging.config import fileConfig
import os
from dotenv import load_dotenv

from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.database import Base
from app.models import db  # ensures models are imported

# Load env FIRST
load_dotenv()

config = context.config

# logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# IMPORTANT: metadata
target_metadata = Base.metadata

# 🔥 FORCE DB URL BEFORE ANYTHING ELSE
db_url = os.getenv("SYNC_DATABASE_URL")

if not db_url:
    raise Exception("SYNC_DATABASE_URL is not set in .env")

config.set_main_option("sqlalchemy.url", db_url)


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
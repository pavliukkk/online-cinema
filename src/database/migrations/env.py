
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[2]),
)

from database.models.base import Base  # noqa: E402
from database.models import movies, accounts  # noqa: E402, F401
from database.session_postgresql import sync_postgresql_engine  # noqa: E402


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    database_url = sync_postgresql_engine.url.render_as_string(
        hide_password=False
    )

    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with sync_postgresql_engine.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

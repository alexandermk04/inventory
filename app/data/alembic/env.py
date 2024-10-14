from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy import pool
from alembic import context

# Import your models and Base here
from tables import Base  # Assuming models.py contains your SQLAlchemy models

# this is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging. This line sets up loggers basically.
fileConfig(config.config_file_name)

# Set your target_metadata (this points to your models' metadata)
target_metadata = Base.metadata

# Load the database URL from the environment variables (or fallback to alembic.ini)
import os
DATABASE_URL = os.getenv('DATABASE_URL')  # Ensure DATABASE_URL is set correctly in your environment

# For dynamic configuration, you can update the `config` object's `set_main_option` with the URL

# Set the SQLAlchemy URL
if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
else:
    raise ValueError("DATABASE_URL environment variable not set")

# Engine creation for connection to the database
def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(config.get_main_option("sqlalchemy.url"), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

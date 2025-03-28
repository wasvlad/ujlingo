import logging
import os
import time
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .models import Base

DATABASE_URL = os.getenv("DATABASE_URL")
if os.getenv("UNIT_TESTS") == "1":
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    MAIN_DATABASE_URL = DATABASE_URL.rsplit('/', 1)[0] + "/postgres"
    engine = create_engine(MAIN_DATABASE_URL, isolation_level="AUTOCOMMIT")
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1 FROM pg_database WHERE datname='unit_tests_database'"))
        if not result.scalar():
            connection.execute(text("CREATE DATABASE unit_tests_database"))
            print("unit_tests_database created.")
        else:
            print("unit_tests_database already exists.")
    DATABASE_URL = DATABASE_URL.rsplit('/', 1)[0] + "/unit_tests_database"
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)

ENVIRONMENT = os.getenv("ENVIRONMENT", None)

if ENVIRONMENT is not None:
    time.sleep(3)

    def run_alembic_migrations():
        """Runs Alembic migrations automatically"""

        # Apply migrations (upgrade to latest version)
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        print("Alembic migrations applied.")

    run_alembic_migrations()
    print("Database is up to date.")

    engine = create_engine(DATABASE_URL)
    DatabaseSession = sessionmaker(bind=engine)

open = None

def get_db():
    global open
    if open is None:
        open = 0
    open += 1
    db = DatabaseSession()
    try:
        yield db  # Provide session to route
    finally:
        db.close()
        open -= 1

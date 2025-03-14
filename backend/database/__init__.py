import os
import time
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
if os.getenv("UNIT_TESTS") == "1":
    DATABASE_URL = "sqlite:///dummy.db"
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

def get_db():
    db = DatabaseSession()
    try:
        yield db  # Provide session to route
    finally:
        db.close()

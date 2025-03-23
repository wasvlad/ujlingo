from database import engine, DatabaseSession
from database.models import Base

def clear_database():
    DatabaseSession.close_all()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

from database import engine
from database.models import Base

def clear_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

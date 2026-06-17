from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker

from app.core.config import settings


engine = create_engine(settings.DB_URL , connect_args={"check_same_thread": False})

session = sessionmaker(autoflush=False , autocommit = False , bind=engine)

Base = declarative_base()


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()








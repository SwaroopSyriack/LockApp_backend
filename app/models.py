from app.core.db import Base
from sqlalchemy import Column , Integer , String  ,DateTime , Boolean ,Text , JSON
from sqlalchemy.orm import relationship
from datetime import datetime , timezone 
import uuid


def get_datetime_utc():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = 'users'
    
    # Use String for UUID in SQLite
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    username = Column(String(255), nullable=True)

    hashed_password = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), default=get_datetime_utc)


class TableRegistery(Base):
    # Here is were all the Tables are stored 
    __tablename__ = "table_registry"

    id = Column(Integer , primary_key = True , autoincrement=True)
    table_name = Column(String(128) , unique=True , nullable=False )
    display_name = Column(String(128) , nullable=True)
    is_default = Column(Boolean , default=False , nullable=True)
    created_at = Column(DateTime , default=datetime.utcnow())
    columns_json = Column(JSON , nullable=False)

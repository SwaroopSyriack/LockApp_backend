from pydantic import BaseModel, EmailStr, Field , field_validator , Json
from typing import Optional, List , Dict ,Any
from datetime import datetime
import uuid
import re


ALLOWED_TYPES = {"TEXT","INTEGER","BIGINT","FLOAT","BOOLEAN","DATE","TIMESTAMP","UUID"}

SAFE_NAME_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]{0,62}$')


def validate_identifier(name : str , label : str):
    if not SAFE_NAME_RE.match(name):
        raise ValueError(f"Invalid {label} {name} Use only letter digits and underscore")
    
    return name.lower()


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    username: Optional[str] = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)

# JSON payload containing access token
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(BaseModel):
    id : Optional[str] = None
    sub: Optional[str] = None


class UserPublic(UserBase):
    user_id: uuid.UUID
    created_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True   # <-- REQUIRED

class UpdatePassword(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class Message(BaseModel):
    message : str = Field(min_length=8, max_length=128)


class ColumnDefinition(BaseModel):
    column_name : str
    data_type : str
    nullable : bool
    default_value : Optional[str] = None


class InsertRowRequest(BaseModel):
    data: List[Dict[str , Any]]
    timedata : str


class CreateTableRequest(BaseModel):
    table_name : str
    display_name : Optional[str]
    columns : list[ColumnDefinition]

    @field_validator("table_name")
    @classmethod
    def clean_table(cls , v):
        return validate_identifier(v , "table name")

    @field_validator("columns")
    @classmethod
    def at_least_column(cls , v):
        if not v:
            raise ValueError("At least one column is Required.")
        names = [c.column_name for c in v ]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate columns are not Allowed")
        return v






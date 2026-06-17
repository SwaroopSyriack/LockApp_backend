from collections.abc import Generator
from typing import Annotated


import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError


from app.core.db import get_db
from app.core.config import settings
from app.core.security import ALGORITHM
from app.schemas import TokenPayload
from app.models import User


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/login/access-token"
)


def get_current_user(db : Annotated[Session , Depends(get_db)] , token : Annotated[str , Depends(reusable_oauth2)]):
    try:
        payload = jwt.decode(token , settings.SECRET_KEY ,  ALGORITHM)
        token_data = TokenPayload(**payload)
    except (InvalidTokenError , ValidationError):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials")
    user = db.get(User, token_data.id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_superuser(current_user: Annotated[User , Depends(get_current_user)]) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
    
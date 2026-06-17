from fastapi import APIRouter, Depends , HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.orm import Session
from datetime import timedelta

from app import crud
from app.core.db import get_db
from app.core.security import create_acess_token
from app.core.config import settings


router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.post("/login" , tags=["Login"])
def login(db : Annotated[Session , Depends(get_db)] , formData : Annotated[OAuth2PasswordRequestForm , Depends()]):
    user = crud.authenticate(db = db , email = formData.username , passwd= formData.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    # Can add also if the user is inactive and will probally add that after sometime

    acess_token = create_acess_token(data = {'id' : str(user.user_id),"sub":user.email} ,expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) )
    return {
        "access_token": acess_token,
        "token_type" : "bearer",
        "username" : user.username
    }



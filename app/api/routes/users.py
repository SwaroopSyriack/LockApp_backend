from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException
from app.core.config import settings
from app.schemas import UserCreate, UserPublic, UpdatePassword, Message
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc
from passlib.context import CryptContext
from typing import List

from app.core.db import get_db
from app.api.deps import get_current_active_superuser, get_current_user
from app.models import User
from app import crud
from app.core.security import get_password_hash
from app.core.security import password_verify


router = APIRouter()


SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = 30


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# The below code is how the data should be their only the admin can view the users , but now i will 
# change that and i will make anyone can , but  future change to admin

# @router.get(
#     "/admin",dependencies=[Depends(get_current_active_superuser)],
#     tags=["Users"] , response_model=List[UserPublic]
# )
# def get_users(
#     db: Annotated[Session, Depends(get_db)],
# ):

# Here the querying is in the modern style like sqlalchemy 2.0  which uses select statement 
@router.get(
    "/admin",dependencies=[Depends(get_current_active_superuser)],
    tags=["Users"] , response_model=List[UserPublic]
)
def get_users(
    db: Annotated[Session, Depends(get_db)],
):
    stmt = (
        select(User)
        .order_by(desc(User.created_at))
    )

    users = db.scalars(stmt).all()

    return users
    


@router.post(
    "/admin", tags=["Users"],response_model=UserPublic 
)
def create_users(
    db: Annotated[Session, Depends(get_db)], create_request: UserCreate
):

    user = crud.get_user_by_email(db=db, email=create_request.email)

    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )

    user_create = User(
        username=create_request.username,
        email=create_request.email,
        hashed_password=get_password_hash(create_request.password),
        is_superuser = create_request.is_superuser
        
    )

    user = crud.create_user(db=db, user_create=user_create)

    return user


@router.get("/me" ,tags=["Users"] , response_model=UserPublic)
def read_user_me(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user


@router.patch("/me", tags=["Users"],response_model=Message)
def update_password_me(
    db: Annotated[Session, Depends(get_db)],
    body: UpdatePassword,
    current_user: Annotated[User, Depends(get_current_user)]
):
    verified, _ = password_verify(body.current_password, current_user.hashed_password)
    if not verified:
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )

    hashed_password = get_password_hash(body.new_password)

    current_user.hashed_password = hashed_password

    db.add(current_user)
    db.commit()

    db.refresh(current_user)

    return Message(message="Password Updated Successfully")


@router.delete("/me", tags=["Users"] ,  response_model=Message)
def delete_user_me(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
):

    if current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Cannot delete SuperUser")

    db.delete(current_user)
    db.commit()
    return Message(message="User Deleted Successfully")



@router.post("/signup", tags=["Users"])
def register_user(
    db: Annotated[Session, Depends(get_db)], create_request: UserCreate
):

    user = crud.get_user_by_email(db=db, email=create_request.email)

    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )

    user_create = User(
        username=create_request.username,
        email=create_request.email,
        hashed_password=get_password_hash(create_request.password),
    )

    user = crud.create_user(db=db, user_create=user_create)

    return user

# @router.get("/user/{id}" , tags=["Users"] )
# def get_user_id(db : Annotated[Session , Depends(get_db)] , current_user : Annotated[User , Depends(get_current_user)]):
#     pass

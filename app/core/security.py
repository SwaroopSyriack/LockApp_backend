from typing import Any, Optional 

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher
from datetime import datetime , timezone  ,timedelta


from app.core.config import settings

password_hash = PasswordHash(
    (
        Argon2Hasher(),
        BcryptHasher(),
    )
)

ALGORITHM = "HS256"

def create_acess_token(data : Any , expires_delta : Optional[timedelta] = None):
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode = data.copy() 
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode , settings.SECRET_KEY , ALGORITHM)


def get_password_hash(password : str) -> str:
    return password_hash.hash(password)

def password_verify(plain_password : str ,hashed_password : str):
    return password_hash.verify_and_update(plain_password  , hashed_password)



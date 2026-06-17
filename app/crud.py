from sqlalchemy import select
from sqlalchemy.orm import Session 
from app.models import User
from app.core.security import password_verify



DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"

def create_user(* , db : Session ,user_create):
    db.add(user_create)
    db.commit()
    db.refresh(user_create)

    return user_create


def authenticate(* , db : Session , email : str , passwd : str) -> User | None:
    db_user = get_user_by_email(db = db , email = email)
    if not db_user:
        password_verify(passwd , DUMMY_HASH)
        return None
        # currently not going to use the updated_password_hash will use in the future its used to update the password hash if any future hashing algorihms comes outt 
    verifed ,  updated_password_hash = password_verify(passwd , db_user.hashed_password)
    if not verifed:
        return None
    return db_user



def get_user_by_email(* , db : Session , email : str) -> User | None:
    return db.query(User).filter(User.email == email).first()



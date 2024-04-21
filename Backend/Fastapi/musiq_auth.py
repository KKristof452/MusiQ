from datetime import datetime, timedelta, timezone
import os
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt


SECRET_KEY = "bd61e585a2b7c8f4086e913938097d49cc9a25b8a33e8e4288fc82cb8833bb95"
ALGORITHM = "HS256"
ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES = 30
STANDARD_ACCESS_TOKEN_EXPIRE_MINUTES = 60


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    username: str
    is_admin: bool = False


class UserAdmin(User):
    hashed_password: str
    is_admin: bool = True


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin_token")


admin_users = {
    os.getenv("ADMIN_USER", "admin"): {
        "username": os.getenv("ADMIN_USER", "admin"),
        "hashed_password": pwd_context.hash(os.getenv("ADMIN_PASS", "MusiQ"))
    }
}

standard_users = {}


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_admin_user(users_db, username):
    if username in users_db:
        user_details = users_db[username]
        return UserAdmin(**user_details)
    

def get_standard_user(standard_users_db, username):
    if username in standard_users_db:
        user_details = standard_users_db[username]
        return User(**user_details)
    

def authenticate_admin_user(users_db, username: str, password: str):
    user = get_admin_user(users_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_user_by_token(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_admin_user(admin_users, username=token_data.username)
    if user:
        return user
    user = get_standard_user(standard_users, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_admin_user(current_user: Annotated[User, Depends(get_user_by_token)]):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not an admin user!")
    return current_user


async def get_current_user(current_user: Annotated[User, Depends(get_user_by_token)]):
    return current_user


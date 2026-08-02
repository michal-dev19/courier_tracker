import bcrypt
import sqlite3
import os
import datetime as dt
from dotenv import load_dotenv
from jose import jwt, JWTError
from pydantic import BaseModel, EmailStr, Field
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Header

# use a router object to route current decorators/function to app in main
router = APIRouter()

# load local .env file
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


# class to receive register/login requests
class CreateUser(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


# hash given user password for storage
def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# token creation upon successful login
def create_token(id):
    return jwt.encode(
        {"sub": id, "exp": dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=3)},
        algorithm=ALGORITHM,
        key=SECRET_KEY,
    )


# authorizes current user
def get_current_user(authorization: str = Header(), conn_curs=Depends(get_db)):
    conn, cursor = conn_curs
    auth_split = authorization.split(" ")
    # splits entire string into bearer variable and token string
    if len(auth_split) == 2 and auth_split[0] == "Bearer":
        bearer, token = auth_split
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")
    # we decode the given token, then check is user still exists in DB
    try:
        payload = jwt.decode(token, algorithms=ALGORITHM, key=SECRET_KEY)
        cursor.execute("SELECT id, email FROM users WHERE id=?", (payload["sub"],))
        user = cursor.fetchone()
        if user is not None:
            return user
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")
    except JWTError:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/register", status_code=201)
# function used to register a user to the database
def register_user(user_info: CreateUser, conn_curs=Depends(get_db)):
    conn, cursor = conn_curs
    try:
        cursor.execute(
            """
        INSERT INTO 
        users (email, password)
        VALUES
        (?, ?)""",
            (user_info.email, hash_password(user_info.password)),
        )
        conn.commit()
        return {"Status": "success"}
    except sqlite3.IntegrityError:
        conn.rollback()
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/login")
# function to log user in and return jwt token
def login_user(user_info: CreateUser, conn_curs=Depends(get_db)):
    conn, cursor = conn_curs
    try:
        cursor.execute(
            """
        SELECT
        id, email, password
        FROM 
        users
        WHERE email=?""",
            (user_info.email,),
        )
        credentials = cursor.fetchone()
    except sqlite3.Error:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    if credentials is None:
        raise HTTPException(status_code=400, detail="Bad Request")
    if bcrypt.checkpw(
        user_info.password.encode("utf-8"), credentials[2].encode("utf-8")
    ):
        return {
            "access_token": create_token(str(credentials[0])),
            "token_type": "bearer",
        }
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.get("/me")
def me(user=Depends(get_current_user)):
    return user

import bcrypt
import sqlite3
from jose import jwt, JWTError
from pydantic import BaseModel
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Header

# use a router object to route current decorators/function to app in main
router = APIRouter()

SECRET_KEY = "F7D8S9B7389B7D9S039UV"
ALGORITHM = "HS256"


# class to receive register/login requests
class CreateUser(BaseModel):
    email: str
    password: str


# hash given user password for storage
def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# token creation upon successful login
def create_token(id):
    try:
        return jwt.encode({"sub": id}, algorithm=ALGORITHM, key=SECRET_KEY)
    except JWTError:
        raise HTTPException(status_code=401, detail="Unauthorized")


# authorizes current user
def get_current_user(authorization=Header()):
    id = authorization.split(" ")[1]
    try:
        return jwt.decode({"sub": id}, algorithms=ALGORITHM, key=SECRET_KEY)
    except JWTError:
        raise HTTPException(status_code=401, detail="Unauthorized")


@router.post("/register")
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
        raise HTTPException(status_code=400, detail="Bad Request")


@router.post("/login")
# function to log user in and return jwt token
def login_user(user_info: CreateUser, conn_curs=Depends(get_db)):
    conn, cursor = conn_curs
    try:
        cursor.execute(
            """
        SELECT
        (id, email, password)
        FROM 
        users
        WHERE email=(?)""",
            (user_info.email,),
        )
        credentials = cursor.fetchone()
        if credentials is None:
            raise HTTPException(status_code=400, detail="Bad Request")
        if bcrypt.checkpw(
            user_info.password.encode("utf-8"), credentials[2].encode("utf-8")
        ):
            return create_token(str(credentials[0]))
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")
    except sqlite3.Error:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/me")
def me(user=Depends(get_current_user)):
    return user

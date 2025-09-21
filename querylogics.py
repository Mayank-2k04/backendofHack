import functions
from db import users
from schemas import User, UserLogin
from fastapi import HTTPException
from createtoken import create_access_token
from datetime import timedelta
from createtoken import ACCESS_TOKEN_EXPIRE_MINUTES


def signup(user: User):
    if users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = functions.hash_password(user.password)

    user_doc = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password,
    }
    result = users.insert_one(user_doc)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create user")

    return {"message": "User registered successfully", "id": str(result.inserted_id)}

def login(user : UserLogin):
    db_user = users.find_one({"email": user.email})
    if not db_user or not functions.verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_access_token(data={"sub": str(db_user["_id"]), "email": user.email, "name": db_user["name"]},
                                expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    return {"access_token": token, "token_type": "bearer"}
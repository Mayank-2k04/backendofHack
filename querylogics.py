from bson import ObjectId
import functions
from db import users, lost_items
from schemas import User, UserLogin, LostItemSchema
from fastapi import File, UploadFile, Form, Depends, HTTPException
from createtoken import create_access_token
from datetime import timedelta
from createtoken import ACCESS_TOKEN_EXPIRE_MINUTES
from auth import get_current_user
import cloudinary.uploader as up
from pydantic import TypeAdapter
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


def add_lost_item(
    title: str = Form(...),
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Upload image to Cloudinary
        result = up.upload(file.file)
        image_url = result["secure_url"]

        # Validate data using Pydantic TypeAdapter
        adapter = TypeAdapter(LostItemSchema)
        lost_item = adapter.validate_python({
            "title": title,
            "description": description,
            "latitude": latitude,
            "longitude": longitude,
            "image_url": image_url
        })

        # Insert into MongoDB with hardcoded user ID
        item_dict = lost_item.model_dump() | {"user_id": ObjectId(current_user["user_id"])}
        item_id = lost_items.insert_one(item_dict).inserted_id

        # Return JSON-safe response
        return {
            "message": "Lost item added!",
            "item_id": str(item_id),
            "image_url": image_url
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from auth import get_current_user
from bson import ObjectId
from db import lost_items, found_items


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def delete_i(item_id: str):
    try:
        oid = ObjectId(item_id)
        print(oid)
        # Delete from both collections (only one will match, but that's fine)
        lost_result = lost_items.delete_one({"_id": oid})

        if lost_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Item not found or you don’t have permission to delete it")

        return {"message": "Item deleted successfully", "item_id": item_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting item: {str(e)}")

def found():
    try:
        items = list(found_items.find())
        # Convert ObjectId to string for JSON response
        for item in items:
            item["_id"] = str(item["_id"])
            item["user_id"] = str(item["user_id"]) if "user_id" in item else None
        return {"found_items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching found items: {str(e)}")

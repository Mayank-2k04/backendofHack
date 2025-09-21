from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class User(BaseModel):
    name: str
    email: EmailStr
    password: str   # later we can hash it

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class LostItemSchema(BaseModel):
    title: str
    description: Optional[str]
    latitude: float
    longitude: float
    image_url: Optional[str] = None
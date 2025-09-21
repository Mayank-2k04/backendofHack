from pydantic import BaseModel, EmailStr


class User(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class LostItemSchema(BaseModel):
    title: str
    description: str
    latitude: float
    longitude: float
    image_url: str
    location: str
    contact: str

class FoundItemSchema(BaseModel):
    title: str
    description: str
    latitude: float
    longitude: float
    image_url: str
    location: str
    contact: str
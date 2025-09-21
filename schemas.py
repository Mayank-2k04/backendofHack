from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class User(BaseModel):
    name: str
    email: EmailStr
    password: str   # later we can hash it

class UserLogin(BaseModel):
    email: EmailStr
    password: str

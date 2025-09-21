from fastapi import FastAPI, HTTPException
from schemas import User, UserLogin
from db import users
from passlib.context import CryptContext
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Campus Safety & Item Recovery")

# Allow requests from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # <-- allow all origins
    allow_credentials=True,
    allow_methods=["*"],        # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],        # Allow all headers
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

@app.post("/signup")
def signup(user: User):
    # Check if user already exists
    if users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_password = hash_password(user.password)

    user_doc = {
        "name": user.name,
        "email": user.email,
        "password": hashed_password,
    }
    result = users.insert_one(user_doc)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create user")

    return {"message": "User registered successfully", "id": str(result.inserted_id)}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@app.post("/login")
def login(user: UserLogin):
    db_user = users.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # Optional: return token instead of message for future auth
    return {"message": f"Login successful for {db_user['name']}", "user_id": str(db_user["_id"])}
from fastapi import FastAPI, Depends
from schemas import User, UserLogin
from fastapi.middleware.cors import CORSMiddleware
import querylogics
from auth import get_current_user

app = FastAPI(title="Campus Safety & Item Recovery")

# Allow requests from anywhere
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # <-- allow all origins
    allow_credentials=True,
    allow_methods=["*"],        # GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],        # Allow all headers
)


@app.post("/signup")
def signup(user: User):
    return querylogics.signup(user)

@app.post("/login")
def login(user: UserLogin):
    return querylogics.login(user)

@app.get("/homepage")
def homepage(current_user: dict = Depends(get_current_user)):
    return current_user



from fastapi import FastAPI, Depends, Form, UploadFile, File
from schemas import User, UserLogin
from fastapi.middleware.cors import CORSMiddleware
import querylogics
from auth import get_current_user
app = FastAPI(title="Campus Safety & Item Recovery")

app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.post("/signup")
def signup(user: User):
    return querylogics.signup(user)

@app.post("/login")
def login(user: UserLogin):
    return querylogics.login(user)

@app.get("/homepage")
def homepage(current_user: dict = Depends(get_current_user)):
    return current_user

@app.post("/lost/add")
async def add_lost(
    title: str = Form(...),
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    return querylogics.add_lost_item(title,description,latitude,longitude,file,current_user)



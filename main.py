from fastapi import FastAPI, Depends, Form, UploadFile, File, HTTPException
from schemas import User, UserLogin
from fastapi.middleware.cors import CORSMiddleware
import querylogics
from auth import get_current_user
app = FastAPI(title="Campus Safety & Item Recovery")
from otpath import send_otp_email, verify_any_otp_and_log

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
def add_lost(
    title: str = Form(...),
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    file: UploadFile = File(...),
    location: str = Form(...),
    contact: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    return querylogics.add_lost_item(title,description,latitude,longitude,file,location,contact,current_user)

@app.post("/found/add")
def add_found_item(
    title: str = Form(...),
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    file: UploadFile = File(...),
    location: str = Form(...),
    contact: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    return querylogics.add_found_item(title,description,latitude,longitude,file,location,contact,current_user)

@app.get("/my/lost")
def get_my_lost_items(current_user: dict = Depends(get_current_user)):
    return querylogics.lost(current_user)

@app.get("/my/found")
def get_my_found_items(current_user: dict = Depends(get_current_user)):
    return querylogics.found(current_user)


@app.post("/send-otp")
def send_otp(
    item_id: str = Form(...),
    item_name: str = Form(...),
    owner_email: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        founder_email = current_user["user_email"]
        result = send_otp_email(item_id, item_name, owner_email, founder_email)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from fastapi import FastAPI, Depends, Form, UploadFile, File, HTTPException
from schemas import User, UserLogin
from fastapi.middleware.cors import CORSMiddleware
import querylogics
from auth import get_current_user
app = FastAPI(title="Campus Safety & Item Recovery")
from otpath import send_otp_email, verify_any_otp_and_log, send_claim_request
import functions
from db import lost_items, found_items
from bson import ObjectId

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

@app.post("/verify-otp")
def verify_otp(otp: str = Form(...)):
    return verify_any_otp_and_log(otp)

@app.delete("/delete-item")
def delete_item(item_id: str = Form(...)):
    return functions.delete_i(item_id)

@app.get("/found-items")
def get_all_found_items(current_user: dict = Depends(get_current_user)):
    return functions.found(current_user)

@app.post("/notify-finder")
def notify_finder(
        item_id: str = Form(...),
        finder_email: str = Form(...),
        current_user: dict = Depends(get_current_user)
):
    claimer_email = current_user["user_email"]
    return send_claim_request(item_id,claimer_email,finder_email)



from searchai import find_matches_for_lost_items



@app.get("/matched-found-items")
def get_matched_found_items(
    current_user: dict=Depends(get_current_user),
    max_distance_km: float = 10,
    min_combined_score: float = 0.6,
    weight_distance: float = 0.3,
    weight_image: float = 0.4,
    weight_text: float = 0.3
):
    """
    Returns matched found items for all lost items of the current user.
    Excludes found items posted by the user.
    """
    try:
        # 1. Get user's lost items
        user_lost_items = list(lost_items.find({"user_id": ObjectId(current_user["user_id"])}))
        if not user_lost_items:
            return {"status": "You have no lost items."}

        # Convert ObjectIds to strings and add 'id' key for matching dictionary
        for li in user_lost_items:
            li["_id"] = str(li["_id"])
            li["id"] = li["_id"]

        # 2. Get all found items excluding user's own
        all_found_items = list(found_items.find({"user_id": {"$ne": ObjectId(current_user["user_id"])}}))
        for fi in all_found_items:
            fi["_id"] = str(fi["_id"])

        # 3. Run matching logic
        matches = find_matches_for_lost_items(
            lost_items=user_lost_items,
            found_items=all_found_items,
            max_distance_km=max_distance_km,
            min_combined_score=min_combined_score,
            weight_distance=weight_distance,
            weight_image=weight_image,
            weight_text=weight_text
        )

        return {"matches": matches}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching matched found items: {str(e)}")

if __name__ == "__main__":
    print(get_matched_found_items(
        {"user_id":"68cf976c2bc42299408548b4"},
        max_distance_km=6
    ))

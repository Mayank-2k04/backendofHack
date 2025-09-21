from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

MONGO_URI = os.getenv("MONGO_URI")
print(MONGO_URI)
client = MongoClient(MONGO_URI)
db = client["cluster0"]

lost_items = db["lost_items"]
found_items = db["found_items"]
alerts = db["alerts"]
handover_requests = db["handover_requests"]
chats = db["chats"]
users = db["users"]
logs = db["logs"]

if __name__ == "__main__":
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

    lost_items.insert_one({
        "title": "Black Wallet",
        "description": "Lost near cafeteria",
        "reporter_email": "student@campus.edu"
    })

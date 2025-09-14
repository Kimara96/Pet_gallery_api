import os
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

CAT_API_KEY = os.getenv("live_bDLrzXE3jRfov2mSKpFyZdVO8Sm2MwRd1McMQFHx7uHxwCgTQbY36OttV7Eei24s")
MONGODB_CONNECTION_STRING = os.getenv("mongodb+srv://pet_gallery_api:pet_gallery_api@grow-c6.zo2rizy.mongodb.net/")

app = FastAPI()

client = MongoClient("mongodb+srv://pet_gallery_api:pet_gallery_api@grow-c6.zo2rizy.mongodb.net/")

db = client["pet_gallery"]

favorites_collection = db["favorites"]
class FavoritePet(BaseModel):
    image_id: str
    image_url: str
    animal_type: str
    

# GET request to fetch a random pet image.
@app.get("/pets/random")
def get_random_pet():
    try:
        headers = {
            'x-api-key': CAT_API_KEY
        }
        # Make a GET request to the Cat API
        response = requests.get("https://api.thecatapi.com/v1/images/search", headers=headers)
        response.raise_for_status()  
        
        # The API returns a list, so we get the first item
        cat_data = response.json()[0]
        image_url = cat_data.get("url")
        image_id = cat_data.get("id")
        return {"image_id": image_id, "image_url": image_url, "animal_type": "cat"}

    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Cat API: {e}")
        raise HTTPException(status_code=500, detail="Could not fetch random cat image")


# POST request to save a favorite pet to the database
@app.post("/pets/favorites")
def save_favorite_pet(favorite: FavoritePet):
    # We insert the pet data into the MongoDB collection
    favorites_collection.insert_one(favorite.model_dump())
    return {"message": "Pet added to favorites successfully"}

# GET request to list all favorite pets from the database
@app.get("/pets/favorites")
def get_all_favorites():
    all_favorites = favorites_collection.find({})
    favorite_list = []
    for pet in all_favorites:
        pet["_id"] = str(pet["_id"])
        favorite_list.append(pet)
    return favorite_list

# DELETE request to remove a favorite pet from the database
@app.delete("/pets/favorites/{image_id}")
def delete_favorite_pet(image_id: str):
    result = favorites_collection.delete_one({"image_id": image_id})
    if result.deleted_count == 1:
        return {"message": f"Pet with image_id {image_id} deleted successfully"}
    else:
        # If nothing was deleted, it means the pet was not found
        raise HTTPException(status_code=404, detail="Pet not found")

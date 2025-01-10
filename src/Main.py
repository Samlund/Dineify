from typing import Annotated
from config import spoonacular_api_key, spotify_api_key, spotify_api_secret

from fastapi import FastAPI, HTTPException, Query, Request, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

import httpx
import base64
import random
app = FastAPI()

app.mount("/static", StaticFiles(directory="./static"), name="static")

templates = Jinja2Templates(directory="./templates")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/",response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


async def fetch_recipe(cuisine: str, course_type: str):
    """
    Fetches information about a recipe from the Spoonacular API based on a specific cuisine and course type.
    :param cuisine: A cuisine, such as "italian"
    :param course_type: A specific type of dish
    :return: JSON containing recipe information
    """
    spoonacular_id = spoonacular_api_key
    spoonacular_url = "https://api.spoonacular.com/recipes/random"
    params = {
        "apiKey": spoonacular_id,
        "tags": f"{cuisine},{course_type}",
        "number": 1,
        "limitLicense": "true",
        "includeNutrition": "false",
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(spoonacular_url, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Server error, please contact support")
    return response.json()

def format_recipe(recipe_data, cuisine: str, course_type: str):
    """
    Extracts and formats recipe data fetched from the Spoonacular API.
    :param recipe_data: Unformatted recipe information
    :param cuisine: A cuisine, such as "italian"
    :param course_type: A specific type of dish
    :return: A dict containing formatted recipe information
    """
    recipe = recipe_data["recipes"][0]
    ingredients = []
    for post in recipe["extendedIngredients"]:
        ingredient = {
            "name": post["name"],
            "amount": post["amount"],
            "unit": post["unit"]
        }
        ingredients.append(ingredient)
    image = "/static/images/default_image.png"
    if "image" in recipe:
        image = recipe["image"]
    return {
        "id": recipe["id"],
        "title": recipe["title"],
        "url": recipe["sourceUrl"],
        "cuisine": cuisine,
        "course": course_type,
        "image": image,
        "servings": recipe["servings"],
        "readyInMinutes": recipe["readyInMinutes"],
        "summary": recipe["summary"],
        "instructions": recipe["instructions"],
        "ingredients": ingredients
    }

def validate_response(recipe_data) -> bool:
    """
    Returns true if a dict containing recipe data is not empty.
    :param recipe_data: dict containing recipe information
    :return: True if dict is not empty, otherwise false
    """
    return bool(recipe_data["recipes"])

@app.get("/v1.0/recipes/")
async def get_menu(cuisine: str, q: Annotated[list[str], Query()] = ["main", "starter", "dessert"], accept: Annotated[str | None, Header()] = None):
    """
    Returns a menu of recipes based on a certain cuisine.
    Method accepts a list of query parameters which specifies which courses will be returned.
    As a default, a three-course menu consisting of a starter, main course and dessert will be returned.
    :param cuisine: A cuisine, such as "italian".
    :param q: A list of courses
    :param accept: Requested media type
    :return: A list of recipes
    """
    if accept != "*/*" and accept != "application/json":
        raise HTTPException(status_code=415, detail="Unsupported media type, only JSON allowed")
    course_type_mapping = {
        "main": "main course",
        "starter": "starter",
        "dessert": "dessert",
    }
    cuisine = cuisine.lower()
    menu = []
    for course in q:
        if course not in course_type_mapping:
            raise HTTPException(status_code=400, detail="Invalid param. Only 'main', 'starter' or 'dessert' allowed")
        else:
            recipe_data = await fetch_recipe(cuisine, course_type_mapping[course])
            if not validate_response(recipe_data):
                recipe_data = await fetch_recipe("", course_type_mapping[course])
                cuisine = "random"
            formatted_recipe = format_recipe(recipe_data, cuisine, course)
            menu.append(formatted_recipe)
    return {"menu": menu}

async def set_token():
    """
    Makes a request to Spotify API to get a bearer token based on Spotify id and secret
    :return: token string
    """
    spotify_id = spotify_api_key
    secret = spotify_api_secret
    user = spotify_id +":" + secret
    user_bytes = base64.b64encode(user.encode('utf-8'))
    user_string = user_bytes.decode('utf-8')
    header = {"Authorization" : "Basic " + user_string
              ,"Content-Type" : "application/x-www-form-urlencoded"}
    body = {"grant_type": "client_credentials"}
    token_url = "https://accounts.spotify.com/api/token"
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, headers = header, data = body)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Server error, please contact support")
        return response.json()["access_token"]

async def get_playlist_id(theme : str):
    """
    Method for getting a random playlist ID from the top 10 Spotify playlists matching the theme
    :param theme: search will be based on this keyword
    :return: playlist id
    """
    token = await set_token()
    request_header = {"Authorization" : "Bearer " + token}
    spotify_endpoint = "https://api.spotify.com/v1/search?q="+theme+"&type=playlist&limit=10"
    async with httpx.AsyncClient() as client:
        response = await client.get(spotify_endpoint, headers=request_header)
        response = response.json()
        response_dict = response["playlists"]["items"]
        option_list = []
        for i in range(response_dict.__len__()):
            if response_dict[i] is not None:
                option_list.append(i)
        index = random.choice(option_list)
        if not option_list:
            return None
        playlist_id = response_dict[index]["id"]
        return playlist_id

@app.get("/v1.0/playlists/")
async def get_playlist(theme : str = None, accept: Annotated[str | None, Header()] = None):
    """
    Returns a playlist ID when get is called on endpoint "/v1.0/playlists/"
    :param theme: theme of the playlist
    :param accept: requested media type from header
    :return: ID for a playlist matching the theme
    """
    if accept != "*/*" and accept != "application/json":
        raise HTTPException(status_code=415, detail="Unsupported media type, only JSON allowed")
    if theme is None:
        raise HTTPException(status_code=400, detail="Please provide a theme as a query. /v1.0/playlists/?theme={theme}")
    _id =  await get_playlist_id(theme)
    if _id is None:
        raise HTTPException(status_code=404, detail="No playlist matching the theme found, try another query")
    return _id

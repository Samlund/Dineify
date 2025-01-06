from typing import Annotated
from config import spoonacular_api_key, spotify_api_key, spotify_api_secret

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import base64
import random
app = FastAPI()

app.mount("/static", StaticFiles(directory="../static"), name="static")

templates = Jinja2Templates(directory="../templates")

@app.get("/",response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

dish_type_mapping = {
    "main": "main course",
    "starter": "starter",
    "dessert": "dessert",
}

async def fetch_recipe(cuisine: str, dish_type: str):
    spoonacular_id = spoonacular_api_key
    spoonacular_url = "https://api.spoonacular.com/recipes/random"
    params = {
        "apiKey": spoonacular_id,
        "tags": f"{cuisine},{dish_type}",
        "number": 1,
        "limitLicense": "true",
        "includeNutrition": "false",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(spoonacular_url, params=params)
            response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=response.status_code, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong")

def format_recipe(recipe_data, cuisine: str, dish_type: str):
    recipe = recipe_data["recipes"][0]
    ingredients = []
    for post in recipe["extendedIngredients"]:
        ingredient = {
            "name": post["name"],
            "amount": post["amount"],
            "unit": post["unit"]
        }
        ingredients.append(ingredient)
    return {
        "id": recipe["id"],
        "title": recipe["title"],
        "url": recipe["sourceUrl"],
        "cuisine": cuisine,
        "course": dish_type,
        "image": recipe["image"],
        "servings": recipe["servings"],
        "readyInMinutes": recipe["readyInMinutes"],
        "summary": recipe["summary"],
        "instructions": recipe["instructions"],
        "ingredients": ingredients
    }

def validate_response(recipe_data) -> bool:
    return bool(recipe_data["recipes"])


@app.get("/v1.0/recipes/menus/")
async def get_menu(cuisine: str, q: Annotated[list[str], Query()] = ["main", "starter", "dessert"]):
    cuisine = cuisine.lower()
    menu = []
    for dish in q:
        if dish not in dish_type_mapping:
            raise HTTPException(status_code=400, detail="Invalid param. Only 'main', 'starter' or 'dessert' allowed")
        else:
            recipe_data = await fetch_recipe(cuisine, dish_type_mapping[dish])
            if not validate_response(recipe_data):
                recipe_data = await fetch_recipe("", dish_type_mapping[dish])

            formatted_recipe = format_recipe(recipe_data, cuisine, dish)
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

async def get_playlist_url(theme : str):
    """
    Method for getting a random playlist from the top 10 Spotify playlists matching the theme
    :param theme: search will be based on this keyword
    :return: URL for an embedded player containing a playlist matching the theme
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
        embedded_url = "https://open.spotify.com/embed/playlist/"+playlist_id+"?utm_source=generator"
        return embedded_url

@app.get("/v1.0/music/playlists/")
async def get_playlist(theme : str):
    """
    Returns a playlist when get is called on endpoint "/v1.0/music/playlists/"
    :param theme: theme of the playlist
    :return: URL for an embedded player containing a playlist matching the theme
    """
    if theme is None:
        raise HTTPException(status_code=400, detail="Please provide a theme as a query. /v1.0/music/playlists/{theme}")
    url =  await get_playlist_url(theme)
    if url is None:
        raise HTTPException(status_code=404, detail="No playlist matching the theme found, try another query")
    return url

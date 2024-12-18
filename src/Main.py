from fastapi import FastAPI, HTTPException
from src.config import spoonacular_api_key
import httpx

app = FastAPI()
spoonacular_api_key = spoonacular_api_key
spoonacular_url = "https://api.spoonacular.com/recipes/random"

async def fetch_recipe(cuisine: str, dish_type: str):
    params = {
        "apiKey": spoonacular_api_key,
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

@app.get("/recipes/mainCourse/")
async def get_main_course(cuisine: str):
    dish_type = "main course"
    recipe_data = await fetch_recipe(cuisine, dish_type)

    recipe = {
        "id": recipe_data["recipes"][0]["id"],
        "title": recipe_data["recipes"][0]["title"],
        "url": recipe_data["recipes"][0]["sourceUrl"],
        "cuisine": f"{cuisine}",
        "dishType": f"{dish_type}",
        "image": recipe_data["recipes"][0]["image"],
        "servings": recipe_data["recipes"][0]["servings"],
        "summary": recipe_data["recipes"][0]["summary"]

    }

    return {"main": recipe}

@app.get("/recipes/starter/")
async def get_starter(cuisine: str):
    dish_type = "starter"
    recipe_data = await fetch_recipe(cuisine, dish_type)

    recipe = {
        "id": recipe_data["recipes"][0]["id"],
         "title": recipe_data["recipes"][0]["title"],
         "url": recipe_data["recipes"][0]["sourceUrl"],
         "cuisine": f"{cuisine}",
         "dishType": f"{dish_type}",
         "image": recipe_data["recipes"][0]["image"],
         "servings": recipe_data["recipes"][0]["servings"],
         "summary": recipe_data["recipes"][0]["summary"]

    }

    return {"starter": recipe}


@app.get("/recipes/dessert/")
async def get_dessert(cuisine: str):
    dish_type = "dessert"
    recipe_data = await fetch_recipe(cuisine, dish_type)

    recipe = {
        "id": recipe_data["recipes"][0]["id"],
        "title": recipe_data["recipes"][0]["title"],
        "url": recipe_data["recipes"][0]["sourceUrl"],
        "cuisine": f"{cuisine}",
        "dishType": f"{dish_type}",
        "image": recipe_data["recipes"][0]["image"],
        "servings": recipe_data["recipes"][0]["servings"],
        "summary": recipe_data["recipes"][0]["summary"]

    }

    return {"dessert": recipe}



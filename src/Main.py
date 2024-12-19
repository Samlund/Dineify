from fastapi import FastAPI, HTTPException
from src.config import spoonacular_api_key
import httpx

app = FastAPI()
spoonacular_api_key = spoonacular_api_key
spoonacular_url = "https://api.spoonacular.com/recipes/random"

dish_type_mapping = {
    "main": "main course",
    "starter": "starter",
    "dessert": "dessert",
}

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

def format_recipe(recipe_data, cuisine: str, dish_type: str):
    recipe = recipe_data["recipes"][0]
    return {
        "id": recipe["id"],
        "title": recipe["title"],
        "url": recipe["sourceUrl"],
        "cuisine": cuisine,
        "dishType": dish_type,
        "image": recipe["image"],
        "servings": recipe["servings"],
        "summary": recipe["summary"],
    }

@app.get("/v1.0/recipes/{dish_type}/")
async def get_recipe(cuisine: str, dish_type: str):
    if dish_type not in dish_type_mapping:
        raise HTTPException(status_code=400, detail="Invalid param. Only 'main', 'starter' or 'dessert' allowed")
    dish_type = dish_type_mapping[dish_type]

    recipe_data = await fetch_recipe(cuisine.capitalize(), dish_type)
    return format_recipe(recipe_data, cuisine, dish_type)



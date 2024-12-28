from typing import Annotated

from fastapi import FastAPI, HTTPException, Query
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
from fastapi import FastAPI, Path, HTTPException
from config import spoonacular_api_key, spotify_api_key, spotify_api_secret, temp_token
from requests import post, get
import asyncio
import base64
import httpx

from fastapi import FastAPI


app = FastAPI()

async def set_token():
    spotify_id = spotify_api_key
    secret = spotify_api_secret
    user = spotify_id +":" + secret
    user_bytes = base64.b64encode(user.encode('utf-8'))
    user_string = user_bytes.decode('utf-8')
    header = {"Authorization" : "Basic " + user_string
              ,"Content-Type" : "application/x-www-form-urlencoded"}
    body = {"grant_type": "client_credentials"}
    token_url = "https://accounts.spotify.com/api/token"
    #response = post(token_url, headers=header, data=body)
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, headers = header, data = body)
        print("Response access token: " + response.json()["access_token"])
        return response.json()["access_token"]

@app.get("/v1.0/music/playlists/")
async def return_playlist(theme : str):
    url =  await get_playlist(theme)
    if url is None:
        raise HTTPException(status_code=404, detail="No playlist matches that theme")
    return url

async def get_playlist(theme : str): #async
    token = await set_token()
    request_header = {"Authorization" : "Bearer " + token}
    spotify_endpoint = "https://api.spotify.com/v1/search?q="+theme+"&type=playlist&limit=1"
    async with httpx.AsyncClient() as client:
        response = await client.get(spotify_endpoint, headers=request_header)
 #   response = response.json()
        print("test")
        print(type(response))
        response = response.json()
        print(type(response))
        print(response)
        response_dict = response["playlists"]["items"]
        print(response_dict)
        playlist_id = response_dict[0]["id"]
        if playlist_id is None:
            return None
        embedded_url = "https://open.spotify.com/embed/playlist/"+playlist_id+"?utm_source=generator"
        return embedded_url


# ändra så att den genererar slumpade spellistor av topplistan
# hur ofta generera nya tokens, varje anrop X

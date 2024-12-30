import random

from fastapi import FastAPI, Path, HTTPException
from pydantic_core.core_schema import none_schema

from config import spoonacular_api_key, spotify_api_key, spotify_api_secret
import base64
import httpx

from fastapi import FastAPI


app = FastAPI()

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
        print("Response access token: " + response.json()["access_token"])
        return response.json()["access_token"]

@app.get("/v1.0/music/playlists/")
async def return_playlist(theme : str):
    """
    Returns a playlist when get is called on endpoint "/v1.0/music/playlists/"
    :param theme: theme of the playlist
    :return: URL for an embedded player containing a playlist matching the theme
    """
    url =  await get_playlist(theme)
    if url is None:
        raise HTTPException(status_code=404, detail="No playlist matches that theme")
    return url



async def get_playlist(theme : str):
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

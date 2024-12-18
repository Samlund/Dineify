from fastapi import FastAPI, Path, HTTPException
from pydantic_core.core_schema import none_schema

from config import spoonacular_api_key, spotify_api_key, spotify_api_secret
from pydantic import BaseModel
from requests import post, get
import base64
import json

from fastapi import FastAPI


app = FastAPI()

def set_token():
    id = spotify_api_key
    secret = spotify_api_secret
    user = id +":" + secret
    user_bytes = base64.b64encode(user.encode('utf-8'))
    user_string = user_bytes.decode('utf-8')
    header = {"Authorization" : "Basic " + user_string
              ,"Content-Type" : "application/x-www-form-urlencoded"}
    body = {"grant_type": "client_credentials"}
    token_url = "https://accounts.spotify.com/api/token"
    response = post(token_url, headers=header, data=body)
    return response.json()["access_token"]

token = set_token()
@app.get("/v1.0/music/playlists/")
def return_playlist(theme : str):
    url = get_playlist(theme)
    if url is None:
        raise HTTPException(status_code=404, detail="No playlist matches that theme")
    return url

def get_playlist(theme : str):
    request_header = {"Authorization" : "Bearer " + token}
    spotify_endpoint = "https://api.spotify.com/v1/search?q="+theme+"&type=playlist&limit=1"
    response = get(spotify_endpoint, headers=request_header).json()
    response_dict = response["playlists"]["items"]
    playlist_id = response_dict[0]["id"]
    if playlist_id is None:
        return None
    embedded_url = "https://open.spotify.com/embed/playlist/"+playlist_id+"?utm_source=generator"
    return embedded_url



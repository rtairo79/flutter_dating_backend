import spotipy
from spotipy.oauth2 import SpotifyOAuth
from django.conf import settings

def get_spotify_client(token=None):
    auth_manager = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-top-read"
    )
    
    if token:
        return spotipy.Spotify(auth=token)
    return spotipy.Spotify(auth_manager=auth_manager)

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import requests
import os


def create_spotify_playlist(sp, song_uris, playlist_name, is_public):
    user_id = sp.current_user()["id"]
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=is_public)
    sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)

def get_billboard_songs(date):
    URL = "https://www.billboard.com/charts/hot-100/"

    response = requests.get(f"{URL}{date}")
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    all_songs = soup.select("li ul li h3")
    song_titles = [song.getText().strip() for song in all_songs]

    return song_titles

def search_songs_spotify(sp, song_titles):
    song_uris = []
    for song in song_titles:
        result = sp.search(q=f"track: {song}", type="track")
        try: 
            uri = result["tracks"]["items"][0]["uri"]
            song_uris.append(uri)
        except IndexError:
            print(f"{song} doesn't exist in Spotify")
    return song_uris

def main():

    load_dotenv()

    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    REDIRECT_URI = os.getenv("REDIRECT_URI")

    date = input("¿A que año quieres viajar? Pon la fecha en el formato AAAA-MM-DD: ")

    try:
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                redirect_uri=REDIRECT_URI,
                scope="playlist-modify-private",
            )
        )

        song_titles = get_billboard_songs(date)
        song_uris = search_songs_spotify(sp, song_titles)

        create_spotify_playlist(sp, song_uris, playlist_name=f"{date} Billboard 100", is_public=False)
    
    except Exception as e:
        print(f"An error ocurred: {str(e)}")

main()
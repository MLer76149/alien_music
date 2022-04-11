import pandas as __pd
import numpy as __np
import matplotlib.pyplot as __plt
from sklearn.preprocessing import StandardScaler as __sc
from sklearn.cluster import KMeans as __km
from sklearn.metrics import silhouette_score as __si
import pickle as __pi
from config import *
import spotipy as __sp
from spotipy.oauth2 import SpotifyClientCredentials



sp = __sp.Spotify(auth_manager=SpotifyClientCredentials(client_id= Client_ID,
                                                           client_secret= Client_SecretID))

hot = __pd.read_csv("data/hot_cluster.csv")
not_hot = __pd.read_csv("data/not_hot_cluster.csv")

# the song will be scaled and clustered and the function returns name, artist, album, picture, songintro
def process_chosen_song(song, artist):
    
    input_id = __get_id(song, artist)
    input_song_df = __song_details(input_id)
    
    if len(input_song_df) != 0:
        song_features = __add_audio_features(input_song_df.iloc[0,0], input_song_df.iloc[0,1])
        scaled_song_features = __standard_scaler(song_features)
        final_song = __predict(scaled_song_features, song_features)
        song_id, hot_or_not = __recommendation(final_song)
        rec_song_df = __song_details(song_id)
        
        return rec_song_df, input_song_df, hot_or_not
    else:
        
        return __pd.DataFrame(), __pd.DataFrame(), ""
    
# search for the entered song
def search_song(song):
    
    if isinstance(song, str):
        song = song.replace("&", "", 3)
        song = song.replace("(", "")
        song = song.replace(")", "")
        results_search_song = sp.search(q="track:"+song, limit=50)
        
    songs = {
    'song': [],
    'artist': [],
    'album': []     
    }
    
    for i in results_search_song["tracks"]["items"]:
        songs['song'].append(i["name"])
        songs['artist'].append(i["album"]["artists"][0]["name"])
        songs['album'].append(i["album"]["name"])

    song_df = __pd.DataFrame(songs)
    
    song_df = song_df[["artist"]].drop_duplicates()

    return song_df

# get song details for display
def __song_details(song_id):
    
    if song_id != "":
        track = sp.track(song_id)

        songs = {
        'song': [],
        'artist': [],
        'album': [],
        'shortcut': [],
        'spotify': [],
        'picture': []
        }

        songs["song"].append(track["name"])
        songs["artist"].append(track["artists"][0]["name"])
        songs["album"].append(track["album"]["name"])
        songs["shortcut"].append(track["preview_url"])
        songs["spotify"].append(track["album"]["artists"][0]["external_urls"]["spotify"])
        songs["picture"].append(track["album"]["images"][0]["url"])

        song_df = __pd.DataFrame(songs)

        return song_df
    
    else:
        return __pd.DataFrame()

# recommend a song based on the userinput
def __recommendation(final_song):
    
    cluster = final_song.iloc[0,-1]
    success = False
    for i, song in enumerate(list(hot["songname"])):
        artist = hot.iloc[i,1]

        if (final_song.iloc[0,0].lower() == song.lower()) and (final_song.iloc[0,1].lower() == artist.lower()):
            recom_hot = hot[(hot["cluster_6_10"] == cluster) & (hot["songname"] != song)].sample()
            success = True
            
            return list(recom_hot["id"])[0], "hot" 
    if success == False:
        recom_not_hot = not_hot[not_hot["cluster_6_10"] == cluster].sample()
        
        return list(recom_not_hot["id"])[0], "fabulous" 


def __add_audio_features(song, artist):

    if song == None or artist == None:
        song = ""
        artist = ""

    test = sp.search(q="track: " + song + " artist: " + artist, limit=1)
    
    if test["tracks"]["items"] != []:

        return __get_audio_features(test["tracks"]["items"][0]["id"])
    else:
        
        return __pd.DataFrame()
    

def __get_audio_features(song):
    
    audio_features = {
    'songname': [],
    'artist': [],
    'album': [],
    'danceability': [],
    'energy': [],
    'key': [],
    'loudness': [],
    'mode': [],
    'speechiness': [],
    'acousticness': [],
    'instrumentalness': [],
    'liveness': [],
    'valence': [],
    'tempo': [],
    'id': [],
    'uri': [],
    'track_href': [],
    'duration_ms': []    
    }
    
    feature = sp.audio_features([song])
    result_track = sp.track(song)
    audio_features['songname'].append(result_track["name"])
    audio_features['artist'].append(result_track["album"]["artists"][0]["name"])
    audio_features['album'].append(result_track["album"]["name"])
    audio_features['danceability'].append(feature[0]['danceability'])
    audio_features['energy'].append(feature[0]['energy'])
    audio_features['key'].append(feature[0]['key'])
    audio_features['loudness'].append(feature[0]['loudness'])
    audio_features['mode'].append(feature[0]['mode'])
    audio_features['speechiness'].append(feature[0]['speechiness'])
    audio_features['acousticness'].append(feature[0]['acousticness'])
    audio_features['instrumentalness'].append(feature[0]['instrumentalness'])
    audio_features['liveness'].append(feature[0]['liveness'])
    audio_features['valence'].append(feature[0]['valence'])
    audio_features['tempo'].append(feature[0]['tempo'])
    audio_features['id'].append(feature[0]['id'])
    audio_features['uri'].append(feature[0]['uri'])
    audio_features['track_href'].append(feature[0]['track_href'])
    audio_features['duration_ms'].append(feature[0]['duration_ms'])
        
    audio_features_df = __pd.DataFrame(audio_features)
        
    return audio_features_df


def __standard_scaler(df):
    
    df_num = df.drop(columns=["songname", "artist", "album", "id", "uri", "track_href"])
    loaded_model = __pi.load(open("scaler/songscaler.sav", 'rb'))
    scaled = loaded_model.transform(df_num)
    scaled_df = __pd.DataFrame(scaled, columns=df_num.columns)
    return scaled_df


def __predict(df_scaled, df_original):
    
    loaded_model = __pi.load(open("models/kmeans_6_10.sav", 'rb'))
    cluster = loaded_model.predict(df_scaled)
    column = "cluster_6_10"
    df_original[column] = cluster
    
    return df_original


def __get_id(song, artist):
    
    if artist == None or song == None:
        return ""
    test = sp.search(q="track: " + song + " artist: " + artist, limit=1)
    
    return test["tracks"]["items"][0]["id"]

    



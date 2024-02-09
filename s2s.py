from googleapiclient.discovery import build
from google.oauth2 import service_account
import time as t
import spotipy as sp
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

SERVICE_ACCOUNT_FILE = 'key.json' #you need to make your own google api for this
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

creds = None
creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES) #make sure to make spotify api details environment variables on your pc

# If modifying these scopes, delete the file token.json.


# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "YOUR-SPREADSHEET-ID" # change depending on sheet make sure to share with api email
RESPONSES = 'songs!' #REMEMBER TO CHANGE THE NAME OF THE RESPONSES IN THE SPREADSHEET TO songs
COLUMN = 'B'
START = '2' #Dont change
END = '100'

#spotipy vars
PLAYLIST_ID = 'YOUR-PLAYLIST-ID' # find playlist id on spotify

scope = 'playlist-modify-public'
username = 'YOUR-SPOTIFY-USERNAME'

song_list = []
playlist_songs = []

token = SpotifyOAuth(scope=scope,username=username)
spotifyObject = sp.Spotify(auth_manager = token)

#prePlaylist = spotifyObject.user_playlist(user=username)
#playlist = prePlaylist['items'][0]['id']

service = build("sheets", "v4", credentials=creds)

# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range = RESPONSES + COLUMN + START + ':' + COLUMN + END).execute()
values = result.get("values", [])
df=pd.DataFrame(values)
df_replace = df.replace([''],[None])
searches = df_replace.values.tolist()
print(searches)

print(RESPONSES + COLUMN + START + ':' + COLUMN + END)

def remove_all_dups():
  j = 0
  p = 0
  while p < len(playlist_songs):
    if playlist_songs.count(playlist_songs[p]) > 1:
      while playlist_songs.count(playlist_songs[p]) > 1:
        playlist_songs.remove(playlist_songs[p])
      p+=1
  print('no dup')
  print(playlist_songs)

  while j < len(song_list):
    #print('length'+str(len(song_list)))
    if song_list.count(song_list[j]) > 1:
      while song_list.count(song_list[j]) > 1:
        print(j)
        print(song_list)
        song_list.remove(song_list[j])
        if playlist_songs.count(song_list[j]) == 1:
          song_list.remove(song_list[j])
      j+=1
  print('no dup')
  print(song_list)
  


i = 0
while True: #keep going infinitely
  result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, 
                             range = RESPONSES + COLUMN + START + ':' + COLUMN + END).execute()
  values = result.get("values", [])
  df=pd.DataFrame(values)
  df_replace = df.replace([''],[None])
  searches = df_replace.values.tolist()
  print(searches)
  #appends all current playlist songs to the list playlist_songs
  TRACKS = spotifyObject.user_playlist_tracks(user=username, playlist_id = PLAYLIST_ID, limit=50) #*******equals the songs in the playlist currently
  for item in TRACKS['items']:
    PLSONGS = item['track']
    playlist_songs.append(PLSONGS['uri'])
  print('playlist_songs')
  print(playlist_songs)

  for item in range(len(searches)): #check every value in array
    if len(searches) == 0: #if cell isnt blank
      t.sleep(10)
    else:  
      SONG = spotifyObject.search(q=searches[item]) #search song
      song_list.append(SONG['tracks']['items'][0]['uri']) #add song to song list
      print(song_list)
    #remove_all_dups()
    '''
    #if values[i] == '': #if the last cell isnt blank 
    END = str(int(END)+1) #expand the range by 1 cell
    START = str(int(START)+1)
    print(RESPONSES + COLUMN + START + ':' + COLUMN + END)
    '''
    #print(i)
  #print('dict')
  print(list(dict.fromkeys(playlist_songs)))
  final_song_list = set(song_list) - set(list(dict.fromkeys(playlist_songs*100)))
  #print('final')
  #print(type(final_song_list))
  if final_song_list != set():
    print(final_song_list)
    spotifyObject.user_playlist_add_tracks(user=username, playlist_id = PLAYLIST_ID, tracks = list(final_song_list))
  song_list.clear()
  final_song_list.clear()
  t.sleep(20) #delay after pinging spotipy
  i = 0
  

from Google import Create_Service
import spotipy as sp
from spotipy.oauth2 import SpotifyOAuth
import time

#Disclaimers:
#If you send too many requests to Spotify it will lock you out for 13 hours
#If you send too many requests to Google it will lock you out for ~60-100 seconds

#Google Stuff
CLIENT_SECRET_FILE = 'key.json' #you need to make your own google api for this
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
API_NAME = 'sheets'
API_VERSION = 'v4'

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "ENTER-SPREADSHEET-ID" # change depending on sheet make sure to share with api email

service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)
sheet = service.spreadsheets()

#Spotify Stuff
PLAYLIST_ID = 'ENTER-PLAYLIST-ID' # find playlist id on spotify
USERNAME = 'ENTER-USERNAME' #check spotify profile for this

scope = 'playlist-modify-public'

spotifyObject = sp.Spotify(auth_manager=SpotifyOAuth(scope=scope))

#gets list of all playlist URIs
def get_playlist_tracks(playlist_id):
    #track songs in playlist
    song_list = []

    #track offset
    offset_var = 0

    #first batch of songs
    TRACKS = spotifyObject.playlist_items(playlist_id, offset=0)

    #while the number of batches the loop runs through is less than the offset
    while offset_var // 100 <= TRACKS['total'] // 100:
        
        #loops over the 100 songs queued in
        for song in range(len(TRACKS['items'])):
            #put the uri in the list
            try:
                song_list.append(TRACKS['items'][song]['track']['uri'])

            #if the song is invalid dont factor it in
            except:
                pass
        
        #queues into the next 100 songs
        offset_var += 100

        #changes tracks to the new queue batch
        TRACKS = spotifyObject.playlist_items(playlist_id, offset=offset_var)
    return song_list

#gets list of all valid spreadsheet song entries
def get_spreadsheet_tracks(spreadsheet_id, sheet_name = 'Form Responses 1', col_start = 'A', col_end = 'C', start = 2, end = 50, limit = 5):
    #vars for collecting entry uris and song names
    uris = []
    names = []

    #by default the range will be A2:C250 which gives enough breathing room for a decent sized playlist that will last a whole event
    #for every run through this loop it will go through 50 entries (aside from the first loop)
    for loops in range(limit):
        #this is collecting the data from the spreadsheet into a variable "result"
        result = sheet.values().get(
            spreadsheetId = spreadsheet_id, 
            range = sheet_name + '!' + col_start + str(start) + ':' + col_end + str(end) #should give something like A2:B50
            ).execute()
        
        #For each entry collected...
        for entry in range(end):
            #try to search for the song in spotify
            try:
                #concatinating into the searching term; should look like "track: {song title} artist: {artist name}"
                song_entry = 'track:' + result['values'][entry][1] + ' artist:' + result['values'][entry][2]

                #verifying that the current entry for the song title isn't blank
                if result['values'][entry][1] != '': 
                    #storing the search results in "SONG"
                    SONG = spotifyObject.search(q = song_entry)
                    
                    #appending the name and uri of the current song to its respective lists
                    uris.append(SONG['tracks']['items'][0]['uri'])
                    names.append(SONG['tracks']['items'][0]['name'])

            #if the song entry is blank or errors...
            except:
                #try to see if there is a spot for the timestamp
                try:
                    #if the timestamp isn't blank it will carry on
                    #the point of this statement is that if a song is manually deleted on the sheet, that it won't error and just skip over it
                    timestamp = result['values'][entry][0]
                    if timestamp == '':
                        return uris, start, end, names
                    
                #if it's just a blank row it'll return what it has
                except:
                    return uris, start, end, names
        
        #if everything is alright, it'll continue onto the next batch (might consider a delay if the API can't keep up)
        start = end + 1
        end += 50

    #this last part is relevant if the API runs out of usage it can only do 100 per 100 secs
    return uris, start, end, names 

#calling the spreadsheet function for the first initial batch
#this is necessary to acquire new_start and new_end
song_uris, new_start, new_end, song_names = get_spreadsheet_tracks(SPREADSHEET_ID)

#Adds songs continuously every 60 seconds, should change to maybe 10 minutes
while True:
    #maps song names to uris; this is used more for debugging and visualization
    song_dict = {}
    for i in range(len(song_uris)):
        song_dict[song_uris[i]] = song_names[i]

    #calling the playlist function to get the songs from the playlist
    playlist_songs = get_playlist_tracks(PLAYLIST_ID)

    #the actual names of the songs added to the playlist
    names_added = [song_dict[entry] for entry in song_uris if entry not in playlist_songs]

    #the uris of the songs added to the playlist
    uris = [entry for entry in song_uris if entry not in playlist_songs]
    
    #leaving this up so that you can see what is added each loop
    print('added', names_added)

    #actually adding the songs to the playlist
    if len(uris) != 0:
        spotifyObject.user_playlist_add_tracks(user= USERNAME, playlist_id = PLAYLIST_ID, tracks = uris)

    #delay over each loop, change depending on use
    time.sleep(60)        

    #getting the new spreadsheet entries where it left off 
    song_entries, new_start, new_end, song_names = get_spreadsheet_tracks(SPREADSHEET_ID, start = new_start, end = new_end)

# Sheets2Spotify

Using Google Sheets API, Spotify API, and Spotipy, I built a program that automatically adds songs from a specific Google Sheet.

It will not catch duplicates on the first run through if any entries are duplicates so you will have to manually delete these in Spotify for the first loop.

You have to create your own API key for Google Sheets and Spotify. 

Make sure you download the OAuth 2.0 Client ID key JSON for your Google API and set environment variables for Spotify API.

Make sure in the Google API that you add your email as a tester or release the app to the public

Set the SPREADSHEET_ID, PLAYLIST_ID, USERNAME variables to your own and run the code, it should take care of the rest when it runs.

Note: When you first run the script you may get a Spotify and Google Pop-up asking you to accept permissions, this is so the app can work.

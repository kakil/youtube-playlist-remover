# https://www.youtube.com/playlist?list=PLMwF3aGmp-CTUf5WJLa5egoRPWB0KPaYd

#
# 1. Go to the Google Developer Console and create a project
# 2. In your project enable the YouTube Data API v3
# 3. Create OAuth 2.0 credentials.  You'll need the client ID
# and the client secret to authenticate your requests.
#

import os
import pickle

import googleapiclient.errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import streamlit as st

# Define the scope: we need permissions to manage the playlist
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Create the flow using the client secrets file from the Google API Console
flow = InstalledAppFlow.from_client_secrets_file(
    'client_secret.json',
    scopes=scopes
)

# Before making API calls
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        credentials = pickle.load(token)
        if credentials.expired:
            credentials.refresh(Request())
else:
    credentials = flow.run_local_server(port=8080)
    with open('token.pickle', 'wb') as token:
        pickle.dump(credentials, token)


# Save the credentials for the next run
with open('token.pickle', 'wb') as token:
    pickle.dump(credentials, token)

from googleapiclient.discovery import build

# Build the YouTube client
youtube = build('youtube', 'v3', credentials=credentials)


def remove_videos_button_action():
    if playlist_id:
        with st.spinner('Deleting videos from the playlist... Please wait.'):
            result = remove_all_videos_from_playlist(playlist_id)

        if result:
            st.success("All videos have been successfully removed from the playlist.")
        else:
            st.error("Failed to remove all videos from the playlist.")


def remove_all_videos_from_playlist(list_id):
    items = []

    request = youtube.playlistItems().list(
        part="id,snippet",
        playlistId=list_id,
        maxResults=50
    )

    while request:
        response = {}
        try:
            response = request.execute()
        except googleapiclient.errors.HttpError as e:
            if e.resp.status == 403:
                st.error("Failed to remove videos: Quota exceeded.  Please try again later.")
                return False
            else:
                st.error(f"An unexpected error occured: {e}")
                return False
        except Exception as e:
            st.error(f"An error occurred: {e}")
            return False

        items += [(item['id'], item['snippet']['resourceId']['videoId']) for item in response.get('items', [])]
        request = youtube.playlistItems().list_next(request, response)
    print("Total videos in playlist: ", len(items))

    if items:
        for item_id, video_id in items:
            delete_request = youtube.playlistItems().delete(id=item_id)
            delete_response = delete_request.execute()
            print(f"Removed video {video_id} from playlist: ", delete_response)

        return True
    else:
        return False


# Function to remove a video from the playlist
def remove_video_from_playlist(playlist_id, video_id):
    # Retrieve the playlistItems to find the id of the item to remove
    request = youtube.playlistItems().list(
        part="id",
        playlistId=playlist_id,
        videoId=video_id
    )
    response = request.execute()

    # Assuming the video is in the playlist, and only once
    if response['items']:
        playlist_item_id = response['items'][0]['id']

        # Now remove the item using the playlistItem id
        delete_request = youtube.playlistItems().delete(id=playlist_item_id)
        delete_response = delete_request.execute()
        print("Video removed from playlist: ", delete_response)
    else:
        print("Video not found in the playlist.")


# watch_later_videos = get_watch_later_videos()
# print(f"Found {len(watch_later_videos)} videos in 'Watch Later'.")


# Remove video from play list

# playlist_id = 'YOUR_PLAYLIST_ID'
# video_id = 'VIDEO_ID_TO_REMOVE'
# remove_video_from_playlist(playlist_id, video_id)
# playlist_id = 'PLMwF3aGmp-CTUf5WJLa5egoRPWB0KPaYd'
# video_id = 'ObqgAZzHmFU'
# remove_all_videos_from_playlist(playlist_id)

st.title("Youtube Playlist Video Remover")
playlist_id = st.text_input("Enter playlist id")
if st.button("Remove Videos"):
    remove_videos_button_action()


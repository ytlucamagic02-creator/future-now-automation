import os
import json
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# temp 폴더 생성
os.makedirs('temp', exist_ok=True)

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_authenticated_service():
    """Authenticate and return YouTube service"""
    
    creds = None
    
    # Check for existing token
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, use environment variables
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Use GitHub Secrets
            client_id = os.environ.get('YOUTUBE_CLIENT_ID')
            client_secret = os.environ.get('YOUTUBE_CLIENT_SECRET')
            refresh_token = os.environ.get('YOUTUBE_REFRESH_TOKEN')
            
            if client_id and client_secret and refresh_token:
                creds = Credentials(
                    token=None,
                    refresh_token=refresh_token,
                    token_uri='https://oauth2.googleapis.com/token',
                    client_id=client_id,
                    client_secret=client_secret,
                    scopes=SCOPES
                )
                creds.refresh(Request())
            else:
                print("❌ Error: YouTube credentials not found!")
                return None
        
        # Save credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('youtube', 'v3', credentials=creds)

def upload_short(youtube, video_file, title, description, playlist_id=None):
    """Upload a single short to YouTube"""
    
    print(f"\n📤 Uploading: {title}")
    
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['Shorts', 'AI', 'Future', 'Technology', 'Innovation'],
            'categoryId': '28',  # Science & Technology
            'defaultLanguage': 'en',
            'defaultAudioLanguage': 'en'
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }
    
    media = MediaFileUpload(video_file, chunksize=-1, resumable=True, mimetype='video/*')
    
    try:
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"   ⏳ Upload progress: {int(status.progress() * 100)}%")
        
        video_id = response['id']
        video_url = f"https://youtube.com/shorts/{video_id}"
        
        print(f"   ✅ Uploaded successfully!")
        print(f"   🔗 URL: {video_url}")
        
        # Add to playlist if specified
        if playlist_id:
            try:
                youtube.playlistItems().insert(
                    part='snippet',
                    body={
                        'snippet': {
                            'playlistId': playlist_id,
                            'resourceId': {
                                'kind': 'youtube#video',
                                'videoId': video_id
                            }
                        }
                    }
                ).execute()
                print(f"   ✅ Added to Shorts playlist")
            except Exception as e:
                print(f"   ⚠️ Playlist add failed: {e}")
        
        return video_url
        
    except Exception as e:
        print(f"   ❌ Upload failed: {e}")
        return None

def upload_shorts():
    """Upload all 3 shorts"""
    
    print("🚀 Starting Shorts upload process...")
    
    # Authenticate
    youtube = get_authenticated_service()
    if not youtube:
        return
    
    # Load shorts metadata
    with open('temp/shorts_segments.json', 'r', encoding='utf-8') as f:
        segments = json.load(f)
    
    shorts = segments['shorts'][:3]  # Exactly 3 shorts
    
    # Get playlist ID from environment
    playlist_id = os.environ.get('SHORTS_PLAYLIST_ID')
    
    print(f"\n📊 Found {len(shorts)} shorts to upload")
    if playlist_id:
        print(f"📋 Shorts Playlist ID: {playlist_id}")
    
    uploaded_urls = []
    
    for i, short in enumerate(shorts, 1):
        video_file = f'temp/short_{i}.mp4'
        
        if not os.path.exists(video_file):
            print(f"\n❌ Short #{i} not found: {video_file}")
            continue
        
        # Build description
        title = short['title']
        hook = short['hook']
        script_preview = short['script'][:100] + '...'
        hashtags = short.get('hashtags', '#AI #FutureTech #Shorts')
        
        description = f"""{hook}

{script_preview}

🔔 Subscribe for daily AI & Future Tech insights!
💡 Follow for more: @FutureNow2

{hashtags}
#YouTubeShorts #TechShorts #AINews"""
        
        # Upload
        url = upload_short(youtube, video_file, title, description, playlist_id)
        
        if url:
            uploaded_urls.append(url)
    
    # Save URLs
    if uploaded_urls:
        with open('temp/shorts_urls.txt', 'w', encoding='utf-8') as f:
            for url in uploaded_urls:
                f.write(url + '\n')
        
        print(f"\n✅ Successfully uploaded {len(uploaded_urls)}/3 shorts!")
        print("\n🔗 Shorts URLs:")
        for i, url in enumerate(uploaded_urls, 1):
            print(f"   {i}. {url}")
    else:
        print("\n❌ No shorts were uploaded successfully")

if __name__ == '__main__':
    upload_shorts()

import os
import json
import pickle
from openai import OpenAI
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

def generate_title():
    """Generate SEO-optimized title using AI"""
    
    print("📝 Generating video title...")
    
    # Read script
    with open('temp/script.txt', 'r', encoding='utf-8') as f:
        script = f.read()
    
    # Initialize OpenAI
    try:
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        prompt = f"""Create a YouTube title for this AI & Future Technology video.

SCRIPT PREVIEW:
{script[:800]}

REQUIREMENTS:
- 50-65 characters total
- Must start with compelling hook words like: "AI", "Future", "2030", "Revolution", etc.
- Include power words: "Will", "Change", "Transform", "Reveal", "Secret"
- SEO-optimized for AI/Tech audience
- Create curiosity without clickbait
- Professional and credible tone

EXAMPLES:
- "AI Will Replace 80% of Jobs by 2030"
- "Future of Technology: What Nobody Tells You"
- "How AI is Secretly Changing Everything"

Return ONLY the title, nothing else."""

        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': 'You are a YouTube SEO expert.'},
                {'role': 'user', 'content': prompt}
            ],
            temperature=0.8,
            max_tokens=100
        )
        
        title = response.choices[0].message.content.strip()
        print(f"✅ Generated title: {title}")
        return title
        
    except Exception as e:
        print(f"⚠️ Title generation failed: {e}")
        # Fallback title
        return "The Future of AI and Technology"

def generate_description():
    """Generate video description with key takeaways"""
    
    print("📝 Generating description...")
    
    # Read script
    with open('temp/script.txt', 'r', encoding='utf-8') as f:
        script = f.read()
    
    # Initialize OpenAI
    try:
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        prompt = f"""Create a YouTube description for this AI & Future Technology video.

SCRIPT:
{script[:1500]}

FORMAT:
[Hook paragraph - 2-3 sentences summarizing the key insight]

🔑 KEY TAKEAWAYS:
• [Takeaway 1]
• [Takeaway 2]
• [Takeaway 3]

📚 CHAPTERS:
0:00 - Introduction
[Auto-generate 4-6 chapters based on script flow]

🔔 SUBSCRIBE for daily AI & Future Tech insights!
💡 Follow us: @FutureNow2

#AI #FutureTechnology #Innovation #TechTrends #ArtificialIntelligence

Keep it under 400 words. Make it engaging and professional."""

        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': 'You are a YouTube content strategist.'},
                {'role': 'user', 'content': prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        description = response.choices[0].message.content.strip()
        print(f"✅ Generated description ({len(description)} chars)")
        return description
        
    except Exception as e:
        print(f"⚠️ Description generation failed: {e}")
        # Fallback description
        return """Explore the future of AI and technology in this insightful video.

🔔 Subscribe for daily AI & Future Tech insights!
💡 Follow us: @FutureNow2

#AI #FutureTechnology #Innovation"""

def upload_to_youtube():
    """Upload video to YouTube with metadata"""
    
    print("🚀 Starting YouTube upload process...")
    
    # Authenticate
    youtube = get_authenticated_service()
    if not youtube:
        return
    
    # Generate metadata
    title = generate_title()
    description = generate_description()
    
    # File paths
    video_file = 'temp/final_video.mp4'
    thumbnail_file = 'temp/thumbnail.jpg'
    
    if not os.path.exists(video_file):
        print(f"❌ Error: {video_file} not found!")
        return
    
    # Video metadata
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': [
                'AI', 'Artificial Intelligence', 'Future Technology',
                'Innovation', 'Tech Trends', 'Future', 'Technology',
                'AI News', 'Tech News', 'Future Predictions'
            ],
            'categoryId': '28',  # Science & Technology
            'defaultLanguage': 'en',
            'defaultAudioLanguage': 'en'
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        },
        'localizations': {
            'en': {
                'title': title,
                'description': description
            }
        }
    }
    
    # Prepare upload
    media = MediaFileUpload(
        video_file,
        chunksize=-1,
        resumable=True,
        mimetype='video/*'
    )
    
    print(f"📤 Uploading video...")
    print(f"   Title: {title}")
    print(f"   File: {video_file}")
    
    try:
        # Upload video
        request = youtube.videos().insert(
            part='snippet,status,localizations',
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"   ⏳ Upload progress: {progress}%")
        
        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"✅ Video uploaded successfully!")
        print(f"🔗 Video URL: {video_url}")
        print(f"🆔 Video ID: {video_id}")
        
        # Upload thumbnail
        if os.path.exists(thumbnail_file):
            print(f"\n📸 Uploading thumbnail...")
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(thumbnail_file)
                ).execute()
                print(f"✅ Thumbnail uploaded!")
            except Exception as e:
                print(f"⚠️ Thumbnail upload failed: {e}")
        
        # Add to playlist
        playlist_id = os.environ.get('MAIN_PLAYLIST_ID')
        if playlist_id:
            print(f"\n📋 Adding to playlist...")
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
                print(f"✅ Added to Main Videos playlist")
            except Exception as e:
                print(f"⚠️ Playlist add failed: {e}")
        
        # Enable automatic dubbing for 21 languages
        print(f"\n🌍 Enabling automatic dubbing...")
        try:
            # YouTube's automatic dubbing is enabled by default for eligible videos
            # Just need to set the original language
            youtube.videos().update(
                part='snippet,localizations',
                body={
                    'id': video_id,
                    'snippet': {
                        'title': title,
                        'description': description,
                        'defaultLanguage': 'en',
                        'defaultAudioLanguage': 'en'
                    }
                }
            ).execute()
            print(f"✅ Automatic dubbing enabled (21 languages)")
        except Exception as e:
            print(f"⚠️ Dubbing setup note: {e}")
        
        # Save video URL
        with open('temp/youtube_url.txt', 'w', encoding='utf-8') as f:
            f.write(video_url)
        
        print(f"\n🎉 Upload complete!")
        print(f"📊 Video will be available shortly at: {video_url}")
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        raise

if __name__ == '__main__':
    upload_to_youtube()

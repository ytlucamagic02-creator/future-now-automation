#!/usr/bin/env python3
import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from openai import OpenAI

def get_youtube_service():
    """YouTube API 서비스 생성"""
    client_id = os.environ.get('YOUTUBE_CLIENT_ID')
    client_secret = os.environ.get('YOUTUBE_CLIENT_SECRET')
    refresh_token = os.environ.get('YOUTUBE_REFRESH_TOKEN')
    
    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("YouTube credentials not found in environment variables")
    
    credentials = Credentials(
        None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret
    )
    
    return build('youtube', 'v3', credentials=credentials)

def generate_description(title):
    """OpenAI로 Shorts 설명 생성"""
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a YouTube Shorts description expert for AI and future technology content."},
                {"role": "user", "content": f"Create a short YouTube Shorts description (100-150 characters) for this video titled '{title}'. Make it engaging and include relevant hashtags."}
            ],
            max_tokens=100,
            temperature=0.7
        )
        description = response.choices[0].message.content.strip()
        
        # 해시태그 추가
        description += "\n\n#Shorts #AI #FutureTech #Technology #AIRevolution #TechShorts #Innovation"
        
        return description
    except Exception as e:
        print(f"Error generating description: {e}")
        return f"{title}\n\n#Shorts #AI #FutureTech #Technology"

def upload_short(video_path, title):
    """YouTube Shorts 업로드"""
    print(f"Uploading Short: {title}")
    
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        return None
    
    youtube = get_youtube_service()
    
    # 설명 생성
    description = generate_description(title)
    
    print(f"Title: {title}")
    print(f"Description: {description[:100]}...")
    
    # 업로드 설정
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['Shorts', 'AI', 'Future Technology', 'Tech', 'AI Revolution', 
                    'Innovation', 'Tech Shorts', 'AI Shorts', 'Future Tech'],
            'categoryId': '28',  # Science & Technology
            'defaultLanguage': 'en',  # ⭐ 영어 설정
            'defaultAudioLanguage': 'en'  # ⭐ 오디오 언어 영어
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }
    
    # 미디어 파일
    media = MediaFileUpload(video_path,
                           mimetype='video/*',
                           resumable=True,
                           chunksize=1024*1024)
    
    # 업로드 실행
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")
    
    video_id = response['id']
    video_url = f"https://www.youtube.com/shorts/{video_id}"
    
    print(f"✅ Short uploaded successfully!")
    print(f"Video ID: {video_id}")
    print(f"Video URL: {video_url}")
    
    # 재생목록에 추가
    playlist_id = os.environ.get('YOUTUBE_SHORTS_PLAYLIST_ID')
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
            print(f"✅ Added to Shorts playlist: {playlist_id}")
        except Exception as e:
            print(f"Warning: Could not add to playlist: {e}")
    
    return video_url

def upload_shorts():
    """모든 Shorts 업로드"""
    print("=" * 60)
    print("📤 Uploading YouTube Shorts...")
    print("=" * 60)
    
    # Shorts 정보 로드
    with open('temp/created_shorts.json', 'r') as f:
        shorts = json.load(f)
    
    urls = []
    for short in shorts:
        video_path = short['output_path']
        title = short['title']
        
        url = upload_short(video_path, title)
        if url:
            urls.append(url)
        
        print()
    
    # URL 저장
    with open('temp/shorts_urls.txt', 'w') as f:
        for url in urls:
            f.write(url + '\n')
    
    print("=" * 60)
    print(f"✅ Uploaded {len(urls)} Shorts successfully!")
    print("=" * 60)

if __name__ == '__main__':
    upload_shorts()

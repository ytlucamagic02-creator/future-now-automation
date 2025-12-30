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

def generate_title():
    """OpenAI로 영상 제목 생성"""
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    
    with open('temp/script.txt', 'r', encoding='utf-8') as f:
        script = f.read()
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a YouTube title expert for AI and future technology content."},
                {"role": "user", "content": f"Based on this script, create a compelling YouTube title (max 100 characters) that will attract viewers interested in AI and future technology:\n\n{script[:500]}"}
            ],
            max_tokens=50,
            temperature=0.7
        )
        title = response.choices[0].message.content.strip()
        return title[:100]  # YouTube 제목 길이 제한
    except Exception as e:
        print(f"Error generating title: {e}")
        return "The Future of AI and Technology"

def generate_description(title):
    """OpenAI로 영상 설명 생성"""
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    
    with open('temp/script.txt', 'r', encoding='utf-8') as f:
        script = f.read()
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a YouTube description expert for AI and future technology content."},
                {"role": "user", "content": f"Create a YouTube description (300-500 characters) for this video titled '{title}':\n\n{script[:1000]}"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        description = response.choices[0].message.content.strip()
        
        # 해시태그 추가
        description += "\n\n#AI #FutureTechnology #ArtificialIntelligence #TechInnovation #FutureTech #AIRevolution #Technology2030 #TechTrends #Innovation #FutureOfAI"
        
        return description
    except Exception as e:
        print(f"Error generating description: {e}")
        return f"{title}\n\nExploring the future of AI and technology.\n\n#AI #FutureTechnology #TechInnovation"

def upload_video():
    """YouTube에 영상 업로드"""
    print("Uploading video to YouTube...")
    
    youtube = get_youtube_service()
    
    # 제목과 설명 생성
    title = generate_title()
    description = generate_description(title)
    
    print(f"Title: {title}")
    print(f"Description: {description[:100]}...")
    
    # 업로드 설정
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': ['AI', 'Artificial Intelligence', 'Future Technology', 'Tech Innovation', 'Future Tech', 
                    'AI Revolution', 'Technology', 'Innovation', 'Tech Trends', '2030'],
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
    media = MediaFileUpload('temp/final_video.mp4', 
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
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    
    print(f"✅ Video uploaded successfully!")
    print(f"Video ID: {video_id}")
    print(f"Video URL: {video_url}")
    
    # URL 저장
    with open('temp/youtube_url.txt', 'w') as f:
        f.write(video_url)
    
    # 재생목록에 추가
    playlist_id = os.environ.get('YOUTUBE_PLAYLIST_ID')
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
            print(f"✅ Added to playlist: {playlist_id}")
        except Exception as e:
            print(f"Warning: Could not add to playlist: {e}")
    
    return video_url

if __name__ == '__main__':
    upload_video()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Shorts 3개 업로드
"""

import os
import sys
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from openai import OpenAI

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_youtube_service():
    """YouTube API 서비스 생성"""
    
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")
    
    if not all([client_id, client_secret, refresh_token]):
        print("❌ YouTube credentials not found!")
        sys.exit(1)
    
    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES
    )
    
    if credentials.expired or not credentials.valid:
        credentials.refresh(Request())
    
    return build('youtube', 'v3', credentials=credentials)

def generate_shorts_description(title):
    """쇼츠 설명 생성"""
    
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    prompt = f"""Create a short YouTube Shorts description (100-150 chars) for this tech topic:

Title: {title}

Requirements:
- Hook viewers in first sentence
- Include 1-2 relevant hashtags
- Keep it concise and engaging
- Tech-focused

Return ONLY the description text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a YouTube Shorts expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=100
        )
        
        description = response.choices[0].message.content.strip()
        
        # 추가 해시태그
        description += "\n\n#Shorts #FutureTech #AI #Technology"
        
        return description
        
    except Exception as e:
        print(f"⚠️ Description generation failed: {e}")
        return f"{title}\n\n#Shorts #FutureTech #AI #Technology"

def upload_short(youtube, video_path, title, playlist_id=None):
    """단일 쇼츠 업로드"""
    
    if not os.path.exists(video_path):
        print(f"   ❌ Video not found: {video_path}")
        return None
    
    # 설명 생성
    description = generate_shorts_description(title)
    
    # 업로드 메타데이터
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': [
                'Shorts', 'AI', 'future tech', 'technology',
                'innovation', 'tech shorts', 'future', 'tech news'
            ],
            'categoryId': '28'  # Science & Technology
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }
    
    try:
        print(f"   📤 Uploading...")
        
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(f"      Progress: {progress}%", end='\r')
        
        video_id = response['id']
        video_url = f"https://www.youtube.com/shorts/{video_id}"
        
        print(f"\n   ✅ Uploaded!")
        print(f"   🔗 {video_url}")
        
        # 재생목록 추가
        if playlist_id:
            try:
                youtube.playlistItems().insert(
                    part="snippet",
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
                print(f"   📋 Added to playlist")
            except Exception as e:
                print(f"   ⚠️ Playlist add failed: {e}")
        
        return video_url
        
    except Exception as e:
        print(f"   ❌ Upload failed: {e}")
        return None

def upload_shorts():
    """메인 함수: 쇼츠 3개 업로드"""
    
    print("📱 Uploading YouTube Shorts...\n")
    
    # 쇼츠 정보 읽기
    try:
        with open("temp/created_shorts.json", "r") as f:
            data = json.load(f)
            shorts = data['shorts']
    except FileNotFoundError:
        print("❌ created_shorts.json not found!")
        sys.exit(1)
    
    # YouTube 서비스
    youtube = get_youtube_service()
    
    # 재생목록 ID
    playlist_id = os.environ.get("YOUTUBE_SHORTS_PLAYLIST_ID")
    
    # 업로드
    uploaded_urls = []
    
    for i, short in enumerate(shorts, 1):
        print(f"[{i}/{len(shorts)}] {short['title']}")
        
        url = upload_short(
            youtube,
            short['path'],
            short['title'],
            playlist_id
        )
        
        if url:
            uploaded_urls.append(url)
        
        print()  # 줄바꿈
    
    # 결과 저장
    if uploaded_urls:
        with open("temp/shorts_urls.txt", "w") as f:
            for url in uploaded_urls:
                f.write(url + "\n")
        
        print(f"✅ Shorts upload completed!")
        print(f"📊 Uploaded {len(uploaded_urls)}/{len(shorts)} shorts")
        print(f"💾 URLs saved to: temp/shorts_urls.txt")
        
        print(f"\n🔗 Shorts URLs:")
        for i, url in enumerate(uploaded_urls, 1):
            print(f"   {i}. {url}")
    else:
        print("❌ No shorts uploaded successfully!")
        sys.exit(1)

if __name__ == "__main__":
    upload_shorts()

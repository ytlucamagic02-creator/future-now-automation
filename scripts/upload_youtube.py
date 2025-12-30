#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 메인 영상 업로드
"""

import os
import sys
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from openai import OpenAI

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def get_youtube_service():
    """YouTube API 서비스 생성"""
    
    print("🔑 Authenticating with YouTube API...")
    
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

def generate_title(script):
    """GPT로 제목 생성"""
    
    print("📝 Generating video title...")
    
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    prompt = f"""Based on this Future Tech video script, create ONE compelling YouTube title.

Script excerpt:
{script[:800]}

Requirements:
- 50-70 characters
- Start with power words: "How", "Why", "What", "Will", "The Future of"
- Include tech keywords: AI, Robot, Quantum, Future, 2030
- Create curiosity or urgency
- Professional but engaging

Examples:
- "Will AI Replace Your Job by 2030?"
- "Quantum Computing: The End of Encryption?"
- "Inside Tesla's Humanoid Robot Factory"
- "How AI Will Change Healthcare Forever"

Return ONLY the title, no quotes, no explanation."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a YouTube SEO expert specializing in tech content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        
        title = response.choices[0].message.content.strip().strip('"').strip("'")
        print(f"✅ Title: {title}")
        return title
        
    except Exception as e:
        print(f"⚠️ Title generation failed: {e}")
        return "The Future of Technology: AI Revolution Explained"

def generate_description(script, title):
    """GPT로 설명 생성"""
    
    print("📝 Generating video description...")
    
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    prompt = f"""Create a YouTube video description for this Future Tech video.

Title: {title}

Script excerpt:
{script[:1000]}

Structure:
1. Opening hook (2 sentences about the topic)
2. What viewers will learn (3-4 bullet points)
3. Call-to-action
4. Hashtags (5-7 relevant tags)

Keep it under 300 words, engaging and SEO-friendly.

Return ONLY the description text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a YouTube SEO expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        description = response.choices[0].message.content.strip()
        
        # 추가 정보
        description += "\n\n━━━━━━━━━━━━━━━━━━━━━━\n"
        description += "🔔 Subscribe for daily tech insights\n"
        description += "💬 Share your thoughts in the comments\n"
        description += "\n#FutureTech #AI #Technology #Innovation #FutureNow"
        
        print(f"✅ Description generated ({len(description)} chars)")
        return description
        
    except Exception as e:
        print(f"⚠️ Description generation failed: {e}")
        return f"{title}\n\nExplore the future of technology with us.\n\n#FutureTech #AI #Technology"

def upload_video():
    """메인 함수: YouTube 업로드"""
    
    print("📤 Uploading video to YouTube...")
    
    # 파일 확인
    video_path = "temp/final_video.mp4"
    thumbnail_path = "temp/thumbnail.jpg"
    
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        sys.exit(1)
    
    # 대본 읽기
    try:
        with open("temp/script.txt", "r", encoding="utf-8") as f:
            script = f.read()
    except FileNotFoundError:
        print("❌ Script not found!")
        sys.exit(1)
    
    # 제목/설명 생성
    title = generate_title(script)
    description = generate_description(script, title)
    
    # YouTube 서비스
    youtube = get_youtube_service()
    
    # 업로드 메타데이터
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': [
                'AI', 'artificial intelligence', 'future technology', 
                'tech news', 'innovation', 'future', 'technology',
                'quantum computing', 'robotics', 'space tech'
            ],
            'categoryId': '28'  # Science & Technology
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }
    
    # 업로드
    print(f"\n📤 Uploading: {title}")
    print(f"📦 File size: {os.path.getsize(video_path)/1024/1024:.1f} MB")
    
    try:
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
                print(f"   Uploading... {progress}%", end='\r')
        
        video_id = response['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        print(f"\n✅ Video uploaded!")
        print(f"🎬 Video ID: {video_id}")
        print(f"🔗 URL: {video_url}")
        
        # URL 저장
        with open("temp/youtube_url.txt", "w") as f:
            f.write(video_url)
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        sys.exit(1)
    
    # 썸네일 업로드
    if os.path.exists(thumbnail_path):
        print("\n🖼️ Uploading thumbnail...")
        
        try:
            youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            
            print("✅ Thumbnail uploaded!")
            
        except Exception as e:
            print(f"⚠️ Thumbnail upload failed: {e}")
    
    # 재생목록에 추가
    playlist_id = os.environ.get("YOUTUBE_PLAYLIST_ID")
    if playlist_id:
        print(f"\n📋 Adding to playlist: {playlist_id}")
        
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
            
            print("✅ Added to playlist!")
            
        except Exception as e:
            print(f"⚠️ Playlist add failed: {e}")
    
    print(f"\n🎉 Upload completed!")
    print(f"🔗 {video_url}")

if __name__ == "__main__":
    upload_video()

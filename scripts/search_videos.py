#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pexels API로 Future Tech B-roll 영상 검색
"""

import os
import sys
import json
import requests
from openai import OpenAI

def extract_keywords(script):
    """GPT로 대본에서 영상 키워드 추출"""
    
    print("🔍 Extracting visual keywords from script...")
    
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    prompt = f"""Extract 16 visual search keywords from this Future Tech script for finding B-roll footage.

Script:
{script[:2000]}

Requirements:
- Focus on VISUAL concepts (things you can SEE and FILM)
- Future tech themes: AI, robots, technology, computers, digital, data, space, innovation
- Cinematic and professional
- Mix of: close-ups, wide shots, abstract concepts
- Each keyword 1-3 words
- In English

Examples:
- "artificial intelligence"
- "robotic arm"
- "data center"
- "futuristic city"
- "quantum computer"
- "space station"
- "holographic display"
- "neural network visualization"

Return EXACTLY 16 keywords, one per line, no numbering, no extra text."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a cinematography expert specializing in tech and science footage."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        keywords_text = response.choices[0].message.content.strip()
        keywords = [k.strip().strip('"').strip("'").strip('-').strip() 
                   for k in keywords_text.split('\n') if k.strip()]
        
        # 정확히 16개 보장
        keywords = keywords[:16]
        while len(keywords) < 16:
            keywords.append("technology innovation")
        
        print(f"✅ Extracted {len(keywords)} keywords")
        for i, kw in enumerate(keywords, 1):
            print(f"   {i}. {kw}")
        
        return keywords
        
    except Exception as e:
        print(f"⚠️ Keyword extraction failed: {e}")
        # 기본 Future Tech 키워드
        return [
            "artificial intelligence", "robot technology", "data center",
            "quantum computer", "futuristic city", "space exploration",
            "holographic display", "neural network", "autonomous vehicle",
            "virtual reality", "biotechnology lab", "smart city",
            "rocket launch", "digital technology", "innovation concept",
            "future technology"
        ]

def search_pexels(keyword, api_key, orientation="landscape", per_page=5):
    """Pexels에서 영상 검색"""
    
    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": api_key}
    params = {
        "query": keyword,
        "orientation": orientation,
        "size": "large",
        "per_page": per_page
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"⚠️ Pexels search failed for '{keyword}': {e}")
        return {"videos": []}

def search_videos():
    """메인 함수: B-roll 영상 검색 및 저장"""
    
    print("🎬 Searching Future Tech B-roll footage on Pexels...")
    
    # API 키 확인
    pexels_api_key = os.environ.get("PEXELS_API_KEY")
    if not pexels_api_key:
        print("❌ PEXELS_API_KEY not found!")
        sys.exit(1)
    
    # 대본 읽기
    try:
        with open("temp/script.txt", "r", encoding="utf-8") as f:
            script = f.read()
    except FileNotFoundError:
        print("❌ Script not found at temp/script.txt")
        sys.exit(1)
    
    # 키워드 추출
    keywords = extract_keywords(script)
    
    # 영상 검색 (키워드당 1개씩, 총 16개)
    all_videos = []
    
    for i, keyword in enumerate(keywords, 1):
        print(f"\n🔍 [{i}/16] Searching: '{keyword}'")
        
        result = search_pexels(keyword, pexels_api_key, per_page=5)
        videos = result.get("videos", [])
        
        if videos:
            # 가장 좋은 영상 선택 (1080p 이상, duration > 5초)
            selected = None
            for video in videos:
                duration = video.get("duration", 0)
                video_files = video.get("video_files", [])
                
                # 1080p 파일 찾기
                hd_files = [vf for vf in video_files 
                           if vf.get("height", 0) >= 1080 and vf.get("width", 0) >= 1920]
                
                if hd_files and duration >= 5:
                    selected = {
                        "id": video.get("id"),
                        "keyword": keyword,
                        "duration": duration,
                        "url": hd_files[0].get("link"),
                        "width": hd_files[0].get("width"),
                        "height": hd_files[0].get("height")
                    }
                    break
            
            if selected:
                all_videos.append(selected)
                print(f"   ✅ Found: {selected['duration']}s, {selected['width']}x{selected['height']}")
            else:
                print(f"   ⚠️ No suitable video found")
        else:
            print(f"   ⚠️ No results")
    
    # 결과 확인
    if len(all_videos) < 10:
        print(f"\n⚠️ Warning: Only {len(all_videos)} videos found (minimum 10 recommended)")
        print("   Filling with backup searches...")
        
        # 백업 키워드로 부족분 채우기
        backup_keywords = [
            "technology abstract", "digital data", "computer network",
            "innovation concept", "futuristic background", "tech visualization"
        ]
        
        for keyword in backup_keywords:
            if len(all_videos) >= 16:
                break
            
            result = search_pexels(keyword, pexels_api_key, per_page=3)
            videos = result.get("videos", [])
            
            for video in videos:
                if len(all_videos) >= 16:
                    break
                
                duration = video.get("duration", 0)
                video_files = video.get("video_files", [])
                hd_files = [vf for vf in video_files if vf.get("height", 0) >= 1080]
                
                if hd_files and duration >= 5:
                    all_videos.append({
                        "id": video.get("id"),
                        "keyword": keyword,
                        "duration": duration,
                        "url": hd_files[0].get("link"),
                        "width": hd_files[0].get("width"),
                        "height": hd_files[0].get("height")
                    })
    
    # 저장
    with open("temp/videos.json", "w", encoding="utf-8") as f:
        json.dump(all_videos, f, indent=2)
    
    total_duration = sum(v["duration"] for v in all_videos)
    print(f"\n✅ Search completed!")
    print(f"📊 Found {len(all_videos)} videos")
    print(f"⏱️ Total duration: {total_duration:.1f} seconds")
    print(f"💾 Saved to: temp/videos.json")
    
    if len(all_videos) < 10:
        print(f"\n⚠️ WARNING: Only {len(all_videos)} videos (need 10+ for 6-8 min video)")
        print("   Video creation may fail or be shorter than expected")

if __name__ == "__main__":
    search_videos()

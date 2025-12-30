#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pexels API로 AI/Future Tech B-roll 영상 검색
"""

import os
import json
import requests
import random
from openai import OpenAI

def extract_keywords():
    """스크립트에서 AI/Tech 키워드 추출"""
    
    # temp 폴더 생성
    os.makedirs('temp', exist_ok=True)
    
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("❌ OPENAI_API_KEY not found!")
    
    client = OpenAI(api_key=api_key)
    
    # 스크립트 읽기
    with open('temp/script.txt', 'r', encoding='utf-8') as f:
        script = f.read()
    
    prompt = f"""You are a video search expert specializing in CINEMATIC AI and technology footage.

Extract 10-12 short English keywords from this AI/Future Tech script for finding professional B-roll video footage on Pexels.

CRITICAL REQUIREMENTS:
- Focus on REAL, CINEMATIC tech visuals (NOT cartoons or animations)
- Prioritize: AI interfaces, robots, futuristic cities, data centers, coding, research labs, modern architecture
- Each keyword should work well with "cinematic" or "futuristic" modifiers
- Avoid: toys, cartoons, abstract art, generic concepts
- IMPORTANT: Use DIVERSE keywords to avoid repetitive footage

GOOD KEYWORD EXAMPLES:
✅ AI robot arm factory
✅ data center servers glowing
✅ programmer coding at night
✅ futuristic city skyline
✅ hologram display interface
✅ quantum computer lab
✅ autonomous car driving
✅ scientist researching technology
✅ modern glass building aerial
✅ neural network visualization
✅ smart city traffic night
✅ space station interior

BAD KEYWORD EXAMPLES (AVOID):
❌ cartoon robot
❌ toy technology
❌ abstract AI
❌ generic computer

Script:
{script[:1500]}

Output ONLY the keywords separated by commas, nothing else.
Focus on REAL, FILMABLE, CINEMATIC tech scenes with VARIETY."""

    print("🔍 Extracting AI/Tech keywords...")
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200
    )
    
    keywords = response.choices[0].message.content.strip()
    print(f"✅ Keywords extracted: {keywords}")
    
    return keywords

def search_pexels_videos(keywords):
    """Pexels API로 다양한 영상 검색"""
    
    api_key = os.environ.get('PEXELS_API_KEY')
    if not api_key:
        raise ValueError("❌ PEXELS_API_KEY not found!")
    
    headers = {'Authorization': api_key}
    
    keyword_list = [k.strip() for k in keywords.split(',')]
    
    video_urls = []
    
    print(f"🎬 Searching Pexels videos... ({len(keyword_list)} keywords)")
    
    # 다양한 스타일
    style_modifiers = [
        'cinematic', 'futuristic', 'modern', 'professional',
        'tech', 'innovative', 'digital', 'advanced'
    ]
    
    # 각 키워드당 2개 영상 = 총 16-20개
    for keyword in keyword_list[:10]:
        modifier = random.choice(style_modifiers)
        search_query = f"{keyword} {modifier}"
        
        random_page = random.randint(1, 5)
        
        try:
            response = requests.get(
                'https://api.pexels.com/videos/search',
                headers=headers,
                params={
                    'query': search_query,
                    'per_page': 3,
                    'orientation': 'landscape',
                    'size': 'large',
                    'page': random_page
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['videos']:
                    count = 0
                    for video in data['videos']:
                        if count >= 2:
                            break
                        
                        duration = video.get('duration', 0)
                        
                        if duration < 10:
                            continue
                        
                        # HD 화질
                        video_file = next(
                            (f for f in video['video_files'] if f['width'] >= 1920),
                            None
                        )
                        
                        if not video_file:
                            continue
                        
                        video_urls.append({
                            'keyword': keyword,
                            'style': modifier,
                            'page': random_page,
                            'url': video_file['link'],
                            'duration': duration,
                            'width': video_file['width'],
                            'height': video_file['height'],
                            'quality': video_file.get('quality', 'hd')
                        })
                        
                        print(f"  ✅ {keyword} ({modifier}, p{random_page}): {video_file.get('quality', 'hd').upper()}")
                        count += 1
                        
                        if len(video_urls) >= 16:
                            break
            
            if len(video_urls) >= 16:
                break
                
        except Exception as e:
            print(f"  ⚠️ {keyword} search failed: {e}")
    
    # 부족하면 추가 검색
    if len(video_urls) < 16:
        print(f"   ℹ️  Only {len(video_urls)} found, searching more...")
        for keyword in keyword_list[len(video_urls) // 2:]:
            if len(video_urls) >= 16:
                break
            
            random_page = random.randint(1, 5)
            
            try:
                response = requests.get(
                    'https://api.pexels.com/videos/search',
                    headers=headers,
                    params={
                        'query': keyword,
                        'per_page': 2,
                        'orientation': 'landscape',
                        'page': random_page
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    for video in data['videos'][:2]:
                        if len(video_urls) >= 16:
                            break
                        
                        video_file = video['video_files'][0]
                        video_urls.append({
                            'keyword': keyword,
                            'style': 'standard',
                            'page': random_page,
                            'url': video_file['link'],
                            'duration': video['duration'],
                            'width': video_file['width'],
                            'height': video_file['height']
                        })
                        print(f"  ✅ {keyword} (standard, p{random_page})")
            except:
                pass
    
    # JSON 저장
    with open('temp/videos.json', 'w', encoding='utf-8') as f:
        json.dump(video_urls, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Total {len(video_urls)} videos found!")
    print(f"   🎬 Cinematic: {sum(1 for v in video_urls if v.get('style') in style_modifiers)}")
    print(f"   📹 Standard: {sum(1 for v in video_urls if v.get('style') == 'standard')}")
    print(f"   📄 Saved: temp/videos.json")
    
    return video_urls

if __name__ == "__main__":
    keywords = extract_keywords()
    search_pexels_videos(keywords)

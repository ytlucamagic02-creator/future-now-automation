#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
롱폼 영상에서 쇼츠 구간 3개 추출
"""

import os
import sys
import json
import ffmpeg
from openai import OpenAI

def extract_shorts_segments(script):
    """GPT로 쇼츠 구간 3개 추출"""
    
    print("✂️ Extracting 3 shorts segments from script...")
    
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    prompt = f"""Identify 3 compelling 30-50 second segments from this Future Tech script for YouTube Shorts.

Full script:
{script}

Each segment should:
- Be self-contained (complete thought)
- Have a HOOK (surprising fact/question)
- Contain valuable insight
- Be 30-50 seconds when spoken
- Work standalone without context

For each segment, provide:
1. Start text (first 3-5 words to identify where it starts)
2. End text (last 3-5 words)
3. Hook title (5-7 words, engaging)
4. Estimated word count

Return as JSON:
{{
  "shorts": [
    {{
      "id": 1,
      "start_text": "first few words...",
      "end_text": "...last few words",
      "title": "Hook Title Here",
      "word_count": 100
    }}
  ]
}}

Return ONLY valid JSON, no markdown, no explanation."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a YouTube Shorts expert. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        shorts = result.get("shorts", [])
        
        if len(shorts) < 3:
            print(f"⚠️ Only {len(shorts)} segments found, expected 3")
        
        print(f"✅ Extracted {len(shorts)} shorts segments:")
        for short in shorts:
            print(f"   #{short['id']}: {short['title']} ({short['word_count']} words)")
        
        return shorts
        
    except Exception as e:
        print(f"❌ Segment extraction failed: {e}")
        sys.exit(1)

def find_timestamp(script, search_text):
    """스크립트에서 텍스트 위치를 찾아 대략적인 타임스탬프 계산"""
    
    # 텍스트 찾기
    pos = script.lower().find(search_text.lower())
    if pos == -1:
        # 부분 일치 시도
        words = search_text.split()
        for i in range(len(words), 0, -1):
            partial = ' '.join(words[:i])
            pos = script.lower().find(partial.lower())
            if pos != -1:
                break
    
    if pos == -1:
        return 0
    
    # 위치를 시간으로 변환 (평균 150 단어/분 = 2.5 단어/초)
    words_before = len(script[:pos].split())
    seconds = words_before / 2.5
    
    return seconds

def extract_shorts():
    """메인 함수: 쇼츠 구간 추출"""
    
    print("✂️ Extracting shorts from main video...")
    
    # 대본 읽기
    try:
        with open("temp/script.txt", "r", encoding="utf-8") as f:
            script = f.read()
    except FileNotFoundError:
        print("❌ Script not found!")
        sys.exit(1)
    
    # 쇼츠 구간 추출
    shorts = extract_shorts_segments(script)
    
    if len(shorts) < 3:
        print("⚠️ Warning: Less than 3 shorts segments")
    
    # 타임스탬프 계산
    segments_with_times = []
    
    for short in shorts[:3]:  # 최대 3개
        start_time = find_timestamp(script, short['start_text'])
        end_time = find_timestamp(script, short['end_text'])
        
        # 최소 길이 보장 (30초)
        if end_time - start_time < 30:
            end_time = start_time + 35
        
        # 최대 길이 제한 (60초)
        if end_time - start_time > 60:
            end_time = start_time + 50
        
        segments_with_times.append({
            'id': short['id'],
            'title': short['title'],
            'start': round(start_time, 2),
            'end': round(end_time, 2),
            'duration': round(end_time - start_time, 2)
        })
        
        print(f"\n📍 Short #{short['id']}: {short['title']}")
        print(f"   Time: {start_time:.1f}s - {end_time:.1f}s (duration: {end_time-start_time:.1f}s)")
    
    # 저장
    output = {'segments': segments_with_times}
    
    with open("temp/shorts_segments.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n✅ Shorts extraction completed!")
    print(f"📊 {len(segments_with_times)} segments identified")
    print(f"💾 Saved to: temp/shorts_segments.json")

if __name__ == "__main__":
    extract_shorts()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DALL-E 3로 썸네일 생성
"""

import os
import sys
import requests
from openai import OpenAI

def generate_thumbnail():
    """대본 기반 썸네일 생성"""
    
    print("🎨 Generating thumbnail with DALL-E 3...")
    
    # OpenAI 클라이언트
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    # 대본 읽기
    try:
        with open("temp/script.txt", "r", encoding="utf-8") as f:
            script = f.read()[:1000]  # 처음 1000자만
    except FileNotFoundError:
        print("❌ Script not found!")
        sys.exit(1)
    
    # 썸네일 프롬프트 생성
    prompt_instruction = f"""Based on this Future Tech video script, create a YouTube thumbnail prompt.

Script excerpt:
{script}

Generate a DALL-E prompt for a striking YouTube thumbnail that:
- Features futuristic technology (AI, robots, holograms, digital interfaces)
- Uses bold neon colors (blue, purple, cyan) with dark background
- Has a cinematic, professional look
- NO TEXT in the image
- Eye-catching and modern design
- Conveys innovation and future technology

Return ONLY the DALL-E prompt, no explanation."""

    try:
        # 썸네일 프롬프트 생성
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert thumbnail designer for tech YouTube channels."},
                {"role": "user", "content": prompt_instruction}
            ],
            temperature=0.8
        )
        
        thumbnail_prompt = response.choices[0].message.content.strip()
        print(f"📝 Thumbnail prompt: {thumbnail_prompt[:100]}...")
        
        # DALL-E 3로 이미지 생성
        print("🎨 Generating image...")
        
        image_response = client.images.generate(
            model="dall-e-3",
            prompt=thumbnail_prompt,
            size="1792x1024",  # YouTube 썸네일 비율
            quality="hd",
            n=1
        )
        
        image_url = image_response.data[0].url
        print(f"✅ Image generated: {image_url}")
        
        # 다운로드
        print("📥 Downloading...")
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()
        
        output_path = "temp/thumbnail.jpg"
        with open(output_path, 'wb') as f:
            f.write(img_response.content)
        
        file_size = os.path.getsize(output_path)
        print(f"\n✅ Thumbnail created!")
        print(f"💾 Saved to: {output_path}")
        print(f"📦 File size: {file_size/1024:.1f} KB")
        print(f"🖼️ Resolution: 1792x1024")
        
    except Exception as e:
        print(f"❌ Thumbnail generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_thumbnail()

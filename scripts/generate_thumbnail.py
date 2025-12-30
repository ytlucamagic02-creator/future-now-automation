#!/usr/bin/env python3
import os
from openai import OpenAI
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

def compress_image_to_limit(image_path, max_size_mb=2):
    """이미지를 2MB 이하로 압축"""
    max_bytes = max_size_mb * 1024 * 1024
    
    img = Image.open(image_path)
    
    # RGBA → RGB 변환
    if img.mode == 'RGBA':
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    
    # 품질 95부터 시작
    quality = 95
    while quality > 20:
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=quality, optimize=True)
        size = buffer.tell()
        
        if size <= max_bytes:
            with open(image_path, 'wb') as f:
                f.write(buffer.getvalue())
            print(f"   ✅ Compression complete: {size / 1024 / 1024:.2f}MB (quality: {quality})")
            return True
        
        quality -= 5
    
    # 해상도 축소
    print(f"   ⚠️  Reducing resolution...")
    img = img.resize((int(img.width * 0.8), int(img.height * 0.8)), Image.Resampling.LANCZOS)
    buffer = BytesIO()
    img.save(buffer, format='JPEG', quality=85, optimize=True)
    
    with open(image_path, 'wb') as f:
        f.write(buffer.getvalue())
    
    final_size = os.path.getsize(image_path)
    print(f"   ✅ Resolution reduced: {final_size / 1024 / 1024:.2f}MB")
    return True

def extract_thumbnail_text():
    """대본에서 썸네일 텍스트 추출 (2-4 단어)"""
    
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return "AI 2030"
    
    client = OpenAI(api_key=api_key)
    
    with open('temp/script.txt', 'r', encoding='utf-8') as f:
        script = f.read()
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a YouTube thumbnail text expert for tech content."
                },
                {
                    "role": "user",
                    "content": f"""Extract 2-4 POWERFUL words for a YouTube thumbnail from this AI/tech script.

Script:
{script[:500]}

REQUIREMENTS:
- 2-4 words ONLY
- ALL CAPS
- Tech-focused and impactful
- Easy to read on mobile
- Related to the main topic

GOOD EXAMPLES:
✅ AI REVOLUTION
✅ FUTURE 2030
✅ QUANTUM LEAP
✅ TECH TAKEOVER
✅ NEXT LEVEL AI

BAD EXAMPLES:
❌ How AI will change everything (too long)
❌ technology (too generic)
❌ Click here (clickbait)

Output ONLY the text, no quotes, no explanation."""
                }
            ],
            max_tokens=20,
            temperature=0.7
        )
        
        text = response.choices[0].message.content.strip()
        text = text.replace('"', '').replace("'", '').upper()
        
        # 최대 4단어로 제한
        words = text.split()[:4]
        text = ' '.join(words)
        
        print(f"   📝 Thumbnail text: {text}")
        return text
        
    except Exception as e:
        print(f"   ⚠️  Text extraction failed: {e}")
        return "AI 2030"

def add_text_to_thumbnail(image_path, text):
    """썸네일에 텍스트 오버레이 추가"""
    img = Image.open(image_path)
    draw = ImageDraw.Draw(img)
    
    width, height = img.size
    
    # 여백
    margin = int(width * 0.1)
    max_text_width = width - (margin * 2)
    
    # 폰트 크기
    font_size = int(width / 10)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
            print("   ⚠️  System font not found, using default")
    
    # 텍스트 크기 계산
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # 텍스트가 너무 길면 폰트 축소
    retry_count = 0
    while text_width > max_text_width and retry_count < 5:
        font_size = int(font_size * 0.85)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        retry_count += 1
        print(f"   🔧 Text too long → font size reduced: {font_size}px")
    
    # 텍스트 위치 (상단 1/3, 중앙)
    x = (width - text_width) / 2
    x = max(margin, min(x, width - margin - text_width))
    y = height / 4
    
    # 검은색 외곽선
    outline_width = max(8, int(font_size / 20))
    for offset_x in range(-outline_width, outline_width + 1):
        for offset_y in range(-outline_width, outline_width + 1):
            if offset_x != 0 or offset_y != 0:
                draw.text((x + offset_x, y + offset_y), text, font=font, fill=(0, 0, 0))
    
    # 흰색 텍스트
    draw.text((x, y), text, font=font, fill=(255, 255, 255))
    
    img.save(image_path, quality=95)
    print(f"   ✅ Text overlay complete: '{text}' (font: {font_size}px)")

def generate_thumbnail():
    """DALL-E 3로 AI/Tech 썸네일 생성"""
    
    # temp 폴더 생성
    os.makedirs('temp', exist_ok=True)
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    # 1단계: 썸네일 텍스트 추출
    print(f"\n🎨 Generating thumbnail...")
    thumbnail_text = extract_thumbnail_text()
    
    # 2단계: 배경 이미지 생성
    prompt = f"""
Create a professional YouTube thumbnail background for an AI and future technology video:

VISUAL STYLE:
- Futuristic, high-tech aesthetic
- Dramatic lighting with neon accents (blue, purple, cyan)
- Focus on AI/robotics/digital technology imagery
- Cinematic, eye-catching composition
- Professional photography style

SUBJECT OPTIONS (choose one):
- AI robot or humanoid with glowing eyes
- Futuristic cityscape with holographic displays
- Neural network visualization with glowing nodes
- High-tech laboratory with advanced equipment
- Digital brain or AI consciousness representation

IMPORTANT: NO TEXT in the image (text will be added separately)

COLOR SCHEME:
- Background: Deep blue, dark purple, or black
- Accent: Neon blue, cyan, or electric purple
- Lighting: Dramatic, high contrast
- Modern, sleek, futuristic

COMPOSITION:
- 16:9 aspect ratio (1280x720)
- Leave top third area clear for text overlay
- Professional, eye-catching
- YouTube thumbnail optimized

STYLE: Futuristic, cinematic, high-tech, professional, clickable
QUALITY: High-detail, photorealistic or stylized 3D render

CRITICAL: NO TEXT, NO WORDS, NO LETTERS in the image
The text will be added programmatically later
"""

    print(f"   🎨 DALL-E 3 generating...")
    
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1792x1024",
        quality="standard",
        n=1
    )
    
    image_url = response.data[0].url
    
    # 다운로드
    print(f"   ⬇️  Downloading...")
    img_data = requests.get(image_url).content
    
    thumbnail_path = 'temp/thumbnail.jpg'
    
    with open(thumbnail_path, 'wb') as f:
        f.write(img_data)
    
    original_size = os.path.getsize(thumbnail_path)
    print(f"   📥 Original size: {original_size / 1024 / 1024:.2f}MB")
    
    # 3단계: 텍스트 오버레이
    print(f"   ✍️  Adding text...")
    add_text_to_thumbnail(thumbnail_path, thumbnail_text)
    
    # 4단계: 2MB 압축
    current_size = os.path.getsize(thumbnail_path)
    if current_size > 2 * 1024 * 1024:
        print(f"   🔧 Over 2MB → compressing...")
        compress_image_to_limit(thumbnail_path, max_size_mb=2)
    else:
        print(f"   ✅ Under 2MB, no compression needed")
    
    final_size = os.path.getsize(thumbnail_path)
    
    print(f"\n✅ Thumbnail generated!")
    print(f"   📁 Saved: {thumbnail_path}")
    print(f"   📊 Final size: {final_size / 1024 / 1024:.2f}MB")
    print(f"   📝 Text: '{thumbnail_text}'")
    
    return thumbnail_path

if __name__ == "__main__":
    generate_thumbnail()

import os
import json
from openai import OpenAI
from pydub.utils import mediainfo

# temp 폴더 생성
os.makedirs('temp', exist_ok=True)

def extract_shorts_segments():
    """Extract 3 shorts segments from the main script using AI"""
    
    print("📝 Extracting shorts segments from script...")
    
    # Read script
    with open('temp/script.txt', 'r', encoding='utf-8') as f:
        script = f.read()
    
    # Get audio duration
    audio_info = mediainfo('temp/audio.mp3')
    audio_duration = float(audio_info['duration'])
    
    print(f"📊 Script length: {len(script)} characters")
    print(f"🎵 Audio duration: {audio_duration:.1f} seconds")
    
    # Initialize OpenAI
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    
    # AI prompt for extracting shorts
    prompt = f"""You are a YouTube Shorts expert for an AI & Future Technology channel.

Extract exactly 3 engaging Shorts segments from this script.

SCRIPT:
{script}

REQUIREMENTS:
- Each Short should be 30-60 seconds of the most captivating content
- Focus on: mind-blowing facts, bold predictions, controversial takes, or "aha!" moments
- Structure: Hook (3-5 sec) → Core insight (20-40 sec) → Mini-CTA (5-10 sec)
- Make titles punchy and curiosity-driven
- Include 3-5 viral hashtags per Short

OUTPUT FORMAT (JSON):
{{
  "shorts": [
    {{
      "title": "AI Will Replace 80% of Jobs by 2030",
      "script": "full segment text (natural sentences, 30-60 seconds worth)",
      "hook": "first sentence that grabs attention",
      "estimated_start_time": 45.0,
      "hashtags": "#AI #FutureTech #JobAutomation"
    }}
  ]
}}

Return ONLY valid JSON, no markdown."""

    # Call OpenAI
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {'role': 'system', 'content': 'You are a YouTube Shorts content strategist.'},
            {'role': 'user', 'content': prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    # Parse response
    result_text = response.choices[0].message.content.strip()
    
    # Remove markdown code blocks if present
    if result_text.startswith('```'):
        result_text = result_text.split('```')[1]
        if result_text.startswith('json'):
            result_text = result_text[4:]
        result_text = result_text.strip()
    
    shorts_data = json.loads(result_text)
    
    # Estimate timestamps based on script position
    script_lower = script.lower()
    for short in shorts_data['shorts']:
        # Try to find hook position in script
        hook_lower = short['hook'].lower()[:50]  # First 50 chars
        pos = script_lower.find(hook_lower)
        
        if pos != -1:
            # Estimate time based on position
            char_rate = len(script) / audio_duration
            estimated_time = pos / char_rate
            short['estimated_start_time'] = round(estimated_time, 1)
        else:
            # Fallback: distribute evenly
            idx = shorts_data['shorts'].index(short)
            short['estimated_start_time'] = round((audio_duration / 4) * (idx + 1), 1)
    
    # Save to file
    with open('temp/shorts_segments.json', 'w', encoding='utf-8') as f:
        json.dump(shorts_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Extracted {len(shorts_data['shorts'])} shorts segments!")
    
    for i, short in enumerate(shorts_data['shorts'], 1):
        print(f"\n📱 Short #{i}:")
        print(f"   Title: {short['title']}")
        print(f"   Start: ~{short['estimated_start_time']}s")
        print(f"   Hook: {short['hook'][:60]}...")

if __name__ == '__main__':
    extract_shorts_segments()

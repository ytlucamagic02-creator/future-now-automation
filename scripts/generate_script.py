#!/usr/bin/env python3
import os
from openai import OpenAI

def generate_script():
    """OpenAI GPT-4o로 Future Tech 주제 스크립트 생성"""
    print("🤖 Generating Future Tech script with GPT-4o...")
    
    # temp 폴더 생성 ⭐ 추가!
    os.makedirs('temp', exist_ok=True)
    
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    
    prompt = """Create an engaging 6-8 minute video script about AI and future technology for 2030.

Requirements:
- Topic: Choose ONE fascinating aspect of AI, quantum computing, robotics, space tech, or metaverse
- Style: Informative, inspiring, forward-thinking
- Length: 1,200-1,500 words
- Tone: Professional yet accessible, like a tech documentary
- Structure: Hook → Context → Main Points (3-4) → Future Impact → Conclusion
- Language: English (US)
- Target audience: Tech enthusiasts, professionals, curious minds

Focus on:
- Real research and current developments
- Specific examples and breakthroughs
- Expert predictions for 2030
- Practical implications for society
- Balance optimism with realistic challenges

Avoid:
- Overly technical jargon
- Sensationalism or fear-mongering
- Generic statements without substance
- Promotional content

Write ONLY the narration script. No titles, no stage directions, just the spoken words."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert science communicator specializing in AI and future technology. You create engaging, accurate, and thought-provoking video scripts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2500,
            temperature=0.8
        )
        
        script = response.choices[0].message.content.strip()
        
        # 스크립트 저장
        with open('temp/script.txt', 'w', encoding='utf-8') as f:
            f.write(script)
        
        print(f"✅ Script generated successfully!")
        print(f"Length: {len(script.split())} words")
        print(f"Preview: {script[:200]}...")
        
        return script
        
    except Exception as e:
        print(f"❌ Error generating script: {e}")
        raise

if __name__ == '__main__':
    generate_script()

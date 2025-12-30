#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Future Now - AI & Tech Script Generator
GPT-4o로 미래 기술 주제 대본 생성 (6-8분, 영어)
"""

import os
import sys
from openai import OpenAI

def generate_script():
    """미래 기술 주제 대본 생성"""
    
    print("🤖 Generating Future Tech script with GPT-4o...")
    
    # OpenAI 클라이언트 초기화
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    # 프롬프트
    prompt = """You are a Future Technology content creator for YouTube.

Create a compelling 6-8 minute video script (1,200-1,500 words) about ONE of these cutting-edge topics:

**AI & Machine Learning:**
- "Will AI Replace Your Job by 2030?"
- "GPT-5: What to Expect from the Next AI Revolution"
- "AI Consciousness: Are We Close to Sentient Machines?"
- "How AI is Transforming Healthcare and Saving Lives"

**Quantum Computing:**
- "Quantum Computers: The End of Encryption?"
- "IBM's Quantum Breakthrough: What It Means for You"
- "Quantum Computing vs Supercomputers: The Ultimate Showdown"

**Metaverse & Virtual Reality:**
- "Is the Metaverse Dead or Just Getting Started?"
- "Apple Vision Pro: The Future of Computing?"
- "Virtual Reality Therapy: Healing in Digital Worlds"

**Robotics & Automation:**
- "Humanoid Robots: Your Future Coworker?"
- "Tesla Bot vs Boston Dynamics: The Robot Wars"
- "Robotic Surgery: Safer Than Human Doctors?"

**Space Technology:**
- "SpaceX Starship: Humanity's Ticket to Mars"
- "Space Mining: The Trillion Dollar Industry"
- "Living on Mars: What Would Daily Life Look Like?"

**SCRIPT REQUIREMENTS:**

1. **Hook (First 15 seconds):**
   - Start with a shocking fact or provocative question
   - Make viewers WANT to keep watching
   - Example: "By 2030, AI could replace 300 million jobs. Is yours safe?"

2. **Structure:**
   - Introduction: Set up the topic (30 seconds)
   - Main Content: 3-4 key points with explanations (5-6 minutes)
   - Conclusion: Summary + future implications (1 minute)

3. **Tone:**
   - Enthusiastic but informative
   - Professional yet accessible
   - Future-focused and optimistic
   - Use analogies for complex topics

4. **Engagement:**
   - Ask rhetorical questions
   - Use "you" to address viewers
   - Include surprising statistics
   - Paint vivid future scenarios

5. **Call-to-Action (End):**
   - "What do you think about this technology?"
   - "Subscribe for more future tech insights"
   - "Let me know in the comments"

6. **Length:** 1,200-1,500 words (6-8 minutes reading time)

7. **Language:** Clear, conversational English

**OUTPUT FORMAT:**
Just the script text, no markdown, no title, no extra formatting. Ready for text-to-speech.

Now generate ONE script on a topic you choose from above."""

    try:
        # GPT-4o 호출
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert Future Technology content creator and science communicator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2500
        )
        
        script = response.choices[0].message.content.strip()
        
        # 스크립트 저장
        with open("temp/script.txt", "w", encoding="utf-8") as f:
            f.write(script)
        
        word_count = len(script.split())
        print(f"✅ Script generated: {word_count} words")
        print(f"📝 Estimated duration: {word_count/150:.1f} minutes")
        print(f"💾 Saved to: temp/script.txt")
        
        # 미리보기 (처음 200자)
        print(f"\n📖 Preview:\n{script[:200]}...\n")
        
        return script
        
    except Exception as e:
        print(f"❌ Error generating script: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_script()

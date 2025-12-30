#!/usr/bin/env python3
import os
from openai import OpenAI

def generate_script():
    """6-8분 분량의 AI/Future Tech 대본 생성"""
    
    # temp 폴더 생성
    os.makedirs('temp', exist_ok=True)
    
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    prompt = """
You are a professional YouTube scriptwriter specializing in AI and future technology content.

Create a complete narration script for a 6-8 minute YouTube video about AI and future technology.

CRITICAL RULES:
1. Write ONLY the narration text that will be spoken
2. DO NOT include any meta information like:
   - Word counts (e.g., "200 words")
   - Time markers (e.g., "1 minute 30 seconds")
   - Section instructions (e.g., "This section should be...")
   - Technical notes or comments
3. DO NOT include section headers like "HOOK:", "INTRO:", etc.
4. Write as one continuous, flowing narration
5. Use NATURAL, ORGANIC transitions between ideas
6. Speak directly to the viewer using "you" and "your"

TARGET LENGTH: 1,500-1,700 words (approximately 8-9 minutes when narrated)

CRITICAL LENGTH REQUIREMENTS:
- The script MUST be at least 1,500 words minimum
- Aim for 1,600-1,700 words for optimal 8-9 minute duration
- Be thorough, detailed, and comprehensive in every section
- Use concrete examples, research findings, and future predictions
- Expand on ideas rather than condensing them

CONTENT STRUCTURE (but don't label these in the script):

1. HOOK (80-100 words / ~30-40 seconds):
   - Start with a mind-blowing fact or provocative question
   - Create curiosity about the future
   - Make it relevant to everyday life
   - Example: "By 2030, AI will change everything about how you work..."

2. CONTEXT (150-200 words / ~60-80 seconds):
   - Current state of the technology
   - Recent breakthroughs or developments
   - Why this matters NOW
   - Real-world examples

3. MAIN CONTENT (700-900 words / ~280-360 seconds):
   - Deep dive into the technology/concept
   - Explain how it works (simply)
   - Future predictions for 2030
   - Real applications and use cases
   - Expert opinions or research findings
   - Balance: optimism + realistic challenges
   
   ⭐ CRITICAL: TRANSITION NATURALLY
   
   GOOD TRANSITION EXAMPLES:
   ✅ "But here's where it gets really interesting..."
   ✅ "So what does this mean for you in 2030?"
   ✅ "Now, imagine this scenario..."
   ✅ "The question everyone's asking is..."
   
   BAD TRANSITIONS (NEVER USE):
   ❌ "Let's transition to..."
   ❌ "Moving on to the next section..."
   ❌ "Now I will explain..."

4. IMPACT & IMPLICATIONS (250-350 words / ~100-140 seconds):
   - How this affects different industries
   - Changes in daily life
   - Opportunities and challenges
   - What you need to know/prepare for

5. CONCLUSION (80-100 words / ~30-40 seconds):
   - Summarize the key takeaway
   - Forward-looking statement
   - Call to action (subscribe, comment)
   - Leave viewer inspired and informed

TONE & STYLE:
- Informative yet accessible
- Enthusiastic but not sensational
- Clear explanations without jargon
- Direct address to viewer
- Professional yet conversational
- Natural flow like a tech journalist

TOPIC SELECTION:
Choose ONE fascinating topic from:
- AI breakthroughs (GPT-5, AGI progress, multimodal AI)
- Quantum computing applications
- Brain-computer interfaces
- Autonomous systems (vehicles, robots, drones)
- Space technology (Mars, space tourism, asteroid mining)
- Metaverse and virtual worlds
- Biotechnology and longevity
- Renewable energy innovations
- Smart cities and IoT
- Future of work with AI

TRANSITION PRINCIPLES:
- Use questions to shift topics naturally
- Use "but", "so", "now", "here's the thing" for smooth flow
- Paint mental pictures
- Make the listener WANT to hear what's next
- Never announce section changes explicitly

IMPORTANT REMINDERS:
- Write ONLY what the narrator will say
- NO technical markers, word counts, or time stamps
- NO section labels or headers
- ONE continuous narrative flow
- Natural transitions between ideas
- PRIORITIZE LENGTH - aim for 1,300+ words
- Better to be detailed than too brief

Choose a unique, timely topic that provides genuine insights about the future of technology.

Begin the script now. Write ONLY the narration text in English.
"""

    print("📝 Future Tech script generation...")
    print("   Model: gpt-4o")
    print("   Target: 1,500-1,700 words (8-9 minutes)")
    print("   Language: English")
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system", 
                "content": "You are a professional YouTube scriptwriter specializing in AI and future technology. Write comprehensive, detailed scripts of at least 1,200 words. Always aim for 1,300+ words. Write ONLY the narration text. Never include meta information, word counts, or section labels. Use NATURAL transitions. Make complex tech accessible and exciting."
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=3000,
        temperature=0.8
    )
    
    script = response.choices[0].message.content.strip()
    
    # 스크립트 저장
    with open('temp/script.txt', 'w', encoding='utf-8') as f:
        f.write(script)
    
    # 통계
    word_count = len(script.split())
    char_count = len(script)
    estimated_time = word_count / 150
    
    print(f"\n✅ Script generated!")
    print(f"   📊  Words: {word_count} (target: 1,500-1,700)")
    
    if word_count < 1500:
        print(f"   ⚠️  Warning: Word count low! ({word_count} < 1,500)")
    elif word_count > 1700:
        print(f"   ℹ️  Note: Longer than target ({word_count} > 1,700)")
    else:
        print(f"   ✅ Word count achieved!")
    
    print(f"   📊 Characters: {char_count}")
    print(f"   ⏱️  Estimated: {estimated_time:.1f} minutes")
    print(f"   📁 Saved: temp/script.txt")
    
    print(f"\n📄 Preview:")
    print(f"   {script[:200]}...")
    
    return script

if __name__ == "__main__":
    generate_script()

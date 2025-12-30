#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Cloud TTS Neural2 오디오 생성
"""

import os
import sys
from google.cloud import texttospeech

def generate_audio():
    """Google TTS Neural2로 오디오 생성"""
    
    print("🎙️ Generating audio with Google Cloud TTS Neural2...")
    
    # Credentials 확인
    credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_path or not os.path.exists(credentials_path):
        print("❌ Google credentials not found!")
        sys.exit(1)
    
    # 대본 읽기
    try:
        with open("temp/script.txt", "r", encoding="utf-8") as f:
            script = f.read().strip()
    except FileNotFoundError:
        print("❌ Script not found at temp/script.txt")
        sys.exit(1)
    
    print(f"📝 Script length: {len(script)} characters")
    print(f"📝 Estimated duration: {len(script)/150/60:.1f} minutes")
    
    # TTS 클라이언트 초기화
    try:
        client = texttospeech.TextToSpeechClient()
    except Exception as e:
        print(f"❌ Failed to initialize TTS client: {e}")
        sys.exit(1)
    
    # 입력 설정
    synthesis_input = texttospeech.SynthesisInput(text=script)
    
    # 음성 설정: Neural2-J (남성, 뉴스 앵커 톤)
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Neural2-J",  # 남성, 전문적 톤
        ssml_gender=texttospeech.SsmlVoiceGender.MALE
    )
    
    # 오디오 설정
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,  # 정상 속도
        pitch=0.0,  # 정상 피치
        effects_profile_id=["headphone-class-device"]  # 고품질
    )
    
    print("🎤 Voice: en-US-Neural2-J (Male, Professional)")
    print("⚙️ Generating audio...")
    
    try:
        # TTS 생성
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # 저장
        output_path = "temp/audio.mp3"
        with open(output_path, "wb") as f:
            f.write(response.audio_content)
        
        # 파일 크기 확인
        file_size = os.path.getsize(output_path)
        print(f"✅ Audio generated successfully!")
        print(f"💾 Saved to: {output_path}")
        print(f"📦 File size: {file_size/1024:.1f} KB")
        
        # 대략적인 길이 추정 (MP3: ~2KB per second at 128kbps)
        estimated_duration = file_size / 2048
        print(f"⏱️ Estimated duration: {estimated_duration:.1f} seconds ({estimated_duration/60:.1f} minutes)")
        
    except Exception as e:
        print(f"❌ TTS generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_audio()

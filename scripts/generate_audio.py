#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Cloud TTS로 대본을 음성(MP3)으로 변환
Neural2-J (Male, News Anchor voice)
"""

import os
import subprocess
from google.cloud import texttospeech

def split_script_smart(script, max_chars=4500):
    """
    스크립트를 자연스럽게 여러 파트로 나누기
    Google TTS는 5000자 제한, 안전하게 4500자로
    """
    if len(script) <= max_chars:
        return [script]
    
    parts = []
    current_pos = 0
    
    while current_pos < len(script):
        end_pos = min(current_pos + max_chars, len(script))
        
        if end_pos < len(script):
            chunk = script[current_pos:end_pos]
            last_period = chunk.rfind('. ')
            
            if last_period > max_chars * 0.7:
                end_pos = current_pos + last_period + 1
        
        parts.append(script[current_pos:end_pos].strip())
        current_pos = end_pos
    
    return parts

def generate_audio_part(client, text, part_num):
    """개별 파트 TTS 생성 (Google Cloud Neural2)"""
    print(f"  🎤 Part {part_num} generating... ({len(text)} chars)")
    
    try:
        # 음성 입력 설정
        synthesis_input = texttospeech.SynthesisInput(text=text)
        
        # 음성 설정: Neural2-J (Male, English US, News Anchor)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Neural2-J",  # Male voice
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )
        
        # 오디오 설정
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,  # 정상 속도
            pitch=0.0  # 정상 음높이
        )
        
        # TTS 실행
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # 파일 저장
        output_path = f'temp/audio_part{part_num}.mp3'
        with open(output_path, 'wb') as out:
            out.write(response.audio_content)
        
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        print(f"  ✅ Part {part_num} completed ({file_size:.2f} MB)")
        
        return output_path
        
    except Exception as e:
        print(f"  ❌ Part {part_num} failed: {e}")
        raise

def merge_audio_files(part_files, output_path):
    """FFmpeg로 여러 MP3 파일 병합"""
    print(f"\n🔗 Merging {len(part_files)} audio files...")
    
    # FFmpeg concat 파일 생성
    concat_file = 'temp/audio_concat.txt'
    with open(concat_file, 'w') as f:
        for part_file in part_files:
            f.write(f"file '{os.path.basename(part_file)}'\n")
    
    # FFmpeg concat
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'audio_concat.txt',
        '-c:a', 'libmp3lame',
        '-b:a', '192k',
        'audio.mp3'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, cwd='temp', text=True)
        
        final_path = 'temp/audio.mp3'
        file_size = os.path.getsize(final_path) / (1024 * 1024)
        print(f"✅ Audio merged! ({file_size:.2f} MB)\n")
        
        return final_path
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Audio merge failed: {e}")
        print(f"FFmpeg stderr: {e.stderr if e.stderr else 'N/A'}")
        raise

def generate_audio():
    """Google Cloud TTS로 오디오 생성"""
    
    # temp 폴더 생성
    os.makedirs('temp', exist_ok=True)
    
    # Google Cloud 클라이언트 초기화
    # GOOGLE_APPLICATION_CREDENTIALS 환경변수 사용
    client = texttospeech.TextToSpeechClient()
    
    # 스크립트 읽기
    with open('temp/script.txt', 'r', encoding='utf-8') as f:
        script = f.read()
    
    print(f"📊 Script length: {len(script)} chars")
    print(f"⏱️ Estimated duration: ~{len(script) / 900:.1f} minutes\n")
    print(f"🎙️ Voice: Google Neural2-J (Male, US English)\n")
    
    # 5000자 제한 대응
    max_chars_per_part = 4500
    
    if len(script) > max_chars_per_part:
        print(f"✂️ Splitting script into parts...\n")
        parts = split_script_smart(script, max_chars_per_part)
        print(f"📋 Split into {len(parts)} parts")
        
        for i, part in enumerate(parts, 1):
            print(f"  Part {i}: {len(part)} chars")
        print()
    else:
        parts = [script]
        print("📋 Single file generation.\n")
    
    # 각 파트별 TTS 생성
    part_files = []
    
    for i, part in enumerate(parts, 1):
        part_file = generate_audio_part(client, part, i)
        part_files.append(part_file)
    
    # 단일 파일이면 그대로, 여러 파일이면 병합
    output_path = 'temp/audio.mp3'
    
    if len(part_files) == 1:
        os.rename(part_files[0], output_path)
        print(f"\n✅ Audio generation completed!")
    else:
        merge_audio_files(part_files, output_path)
        
        # 임시 파일 정리
        for part_file in part_files:
            if os.path.exists(part_file):
                os.remove(part_file)
        if os.path.exists('temp/audio_concat.txt'):
            os.remove('temp/audio_concat.txt')
    
    final_size = os.path.getsize(output_path) / (1024 * 1024)
    
    # FFprobe로 정확한 길이 측정
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', output_path],
            capture_output=True,
            text=True,
            check=True
        )
        duration = float(result.stdout.strip())
        duration_min = duration / 60
        print(f"📄 Final file: {output_path}")
        print(f"📊 Size: {final_size:.2f} MB")
        print(f"⏱️  Duration: {duration_min:.1f} minutes ({duration:.0f}s)")
    except:
        print(f"📄 Final file: {output_path}")
        print(f"📊 Size: {final_size:.2f} MB")
    
    print(f"🎉 8-9 minute audio generated!\n")
    
    return output_path

if __name__ == "__main__":
    generate_audio()

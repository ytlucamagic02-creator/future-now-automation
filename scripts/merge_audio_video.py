#!/usr/bin/env python3
"""
무음 영상 + 음성을 병합하여 최종 영상 생성
"""

import os
import sys
import subprocess
from pathlib import Path

def get_duration(file_path):
    """FFprobe로 파일 길이 가져오기"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
            capture_output=True,
            text=True,
            check=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        print(f"⚠️ Duration check failed for {file_path}: {e}")
        return 0.0

def merge_audio_video():
    """영상과 음성 병합"""
    print("\n" + "=" * 60)
    print("🔗 Merging audio and video")
    print("=" * 60)
    
    # temp 폴더 생성
    os.makedirs('temp', exist_ok=True)
    
    video_path = Path('temp/silent_video.mp4')
    audio_path = Path('temp/audio.mp3')
    output_path = Path('temp/final_video.mp4')
    
    # 파일 존재 확인
    if not video_path.exists():
        print(f"❌ Video file not found: {video_path}")
        sys.exit(1)
    
    if not audio_path.exists():
        print(f"❌ Audio file not found: {audio_path}")
        sys.exit(1)
    
    # 길이 확인
    video_duration = get_duration(str(video_path))
    audio_duration = get_duration(str(audio_path))
    
    print(f"\n📊 File info:")
    print(f"   🎬 Video: {video_duration / 60:.1f} minutes")
    print(f"   🎙️ Audio: {audio_duration / 60:.1f} minutes")
    
    # 길이 차이 경고
    duration_diff = abs(video_duration - audio_duration)
    if duration_diff > 30:
        print(f"\n⚠️ Warning: Duration difference > 30 seconds ({duration_diff:.1f}s)")
        print(f"   Video will be trimmed/extended to match audio")
    
    # FFmpeg 병합
    print(f"\n🔗 Merging...")
    
    try:
        # 오디오 길이에 맞춰 영상 조정
        cmd = [
            'ffmpeg', '-y',
            '-i', str(video_path),
            '-i', str(audio_path),
            '-filter_complex', f'[0:v]setpts={audio_duration/video_duration}*PTS[v]',
            '-map', '[v]',
            '-map', '1:a',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-shortest',
            str(output_path)
        ]
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print(f"✅ Merge completed!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Merge failed!")
        print(f"   FFmpeg stderr: {e.stderr[:500]}")
        sys.exit(1)
    
    # 최종 확인
    if not output_path.exists():
        print(f"\n❌ Final video not created!")
        sys.exit(1)
    
    final_duration = get_duration(str(output_path))
    final_size = output_path.stat().st_size / (1024 * 1024)
    
    print(f"\n" + "=" * 60)
    print(f"🎉 Final video created!")
    print(f"=" * 60)
    print(f"   📁 File: {output_path}")
    print(f"   📊 Size: {final_size:.1f} MB")
    print(f"   ⏱️  Duration: {final_duration / 60:.1f} minutes ({final_duration:.0f}s)")
    print(f"   🎬 Video + Audio merged!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        merge_audio_video()
    except KeyboardInterrupt:
        print("\n\n⚠️ User interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

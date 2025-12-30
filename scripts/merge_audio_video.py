#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
오디오와 영상 합성
"""

import os
import sys
import ffmpeg

def merge_audio_video():
    """오디오와 무음 영상을 합성하여 최종 영상 생성"""
    
    print("🎵 Merging audio and video...")
    
    # 파일 존재 확인
    video_path = "temp/silent_video.mp4"
    audio_path = "temp/audio.mp3"
    output_path = "temp/final_video.mp4"
    
    if not os.path.exists(video_path):
        print(f"❌ Video not found: {video_path}")
        sys.exit(1)
    
    if not os.path.exists(audio_path):
        print(f"❌ Audio not found: {audio_path}")
        sys.exit(1)
    
    # 길이 확인
    try:
        video_probe = ffmpeg.probe(video_path)
        audio_probe = ffmpeg.probe(audio_path)
        
        video_duration = float(video_probe['streams'][0]['duration'])
        audio_duration = float(audio_probe['streams'][0]['duration'])
        
        print(f"📹 Video duration: {video_duration:.1f}s ({video_duration/60:.1f} min)")
        print(f"🎙️ Audio duration: {audio_duration:.1f}s ({audio_duration/60:.1f} min)")
        
        # 길이 차이 확인
        diff = abs(video_duration - audio_duration)
        if diff > 30:
            print(f"⚠️ Warning: Duration mismatch: {diff:.1f}s")
        
    except Exception as e:
        print(f"⚠️ Could not probe durations: {e}")
    
    # 합성
    print("⚙️ Merging...")
    
    try:
        video_input = ffmpeg.input(video_path)
        audio_input = ffmpeg.input(audio_path)
        
        (
            ffmpeg
            .output(
                video_input.video,
                audio_input.audio,
                output_path,
                vcodec='copy',  # 영상 재인코딩 안 함 (빠름)
                acodec='aac',
                audio_bitrate='192k',
                shortest=None  # 오디오 길이에 맞춤
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        # 결과 확인
        file_size = os.path.getsize(output_path)
        final_probe = ffmpeg.probe(output_path)
        final_duration = float(final_probe['streams'][0]['duration'])
        
        print(f"\n✅ Merge completed!")
        print(f"💾 Saved to: {output_path}")
        print(f"📦 File size: {file_size/1024/1024:.1f} MB")
        print(f"⏱️ Final duration: {final_duration:.1f}s ({final_duration/60:.1f} min)")
        print(f"🎞️ Resolution: 1920x1080")
        print(f"🎵 Audio: AAC 192kbps")
        
    except ffmpeg.Error as e:
        print(f"❌ Merge failed: {e.stderr.decode()}")
        sys.exit(1)

if __name__ == "__main__":
    merge_audio_video()

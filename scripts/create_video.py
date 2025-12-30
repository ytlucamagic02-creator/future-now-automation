#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
무음 영상 생성 (1920x1080, B-roll 조합)
"""

import os
import sys
import json
import requests
import ffmpeg

def download_video(url, output_path):
    """영상 다운로드"""
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        print(f"   ⚠️ Download failed: {e}")
        return False

def create_video():
    """B-roll 영상들을 조합하여 무음 영상 생성"""
    
    print("🎬 Creating silent video from B-roll footage...")
    
    # videos.json 읽기
    try:
        with open("temp/videos.json", "r", encoding="utf-8") as f:
            videos = json.load(f)
    except FileNotFoundError:
        print("❌ videos.json not found!")
        sys.exit(1)
    
    if len(videos) < 8:
        print(f"❌ Not enough videos: {len(videos)} (need at least 8)")
        sys.exit(1)
    
    print(f"📹 Processing {len(videos)} video clips...")
    
    # 영상 다운로드 및 처리
    downloaded_files = []
    target_duration = 480  # 8분 목표
    
    for i, video in enumerate(videos, 1):
        video_path = f"temp/clip_{i}.mp4"
        
        print(f"\n[{i}/{len(videos)}] {video['keyword']}")
        print(f"   Duration: {video['duration']}s")
        print(f"   Downloading...")
        
        if download_video(video['url'], video_path):
            downloaded_files.append({
                'path': video_path,
                'duration': video['duration']
            })
            print(f"   ✅ Downloaded")
        else:
            print(f"   ⚠️ Skipped")
    
    if len(downloaded_files) < 8:
        print(f"\n❌ Only {len(downloaded_files)} videos downloaded (need 8+)")
        sys.exit(1)
    
    print(f"\n✅ Downloaded {len(downloaded_files)} clips")
    
    # 총 길이 계산
    total_duration = sum(clip['duration'] for clip in downloaded_files)
    print(f"📊 Total raw duration: {total_duration:.1f}s ({total_duration/60:.1f} min)")
    
    # 각 클립을 목표 길이에 맞게 사용
    # 목표: 8분 = 480초, 16개 클립 = 각 30초씩
    clips_per_duration = target_duration / len(downloaded_files)
    print(f"⚙️ Target per clip: {clips_per_duration:.1f}s")
    
    # FFmpeg concat 파일 생성
    concat_file = "temp/video_concat.txt"
    processed_clips = []
    
    for i, clip in enumerate(downloaded_files, 1):
        input_path = clip['path']
        output_path = f"temp/processed_{i}.mp4"
        clip_duration = min(clip['duration'], clips_per_duration)
        
        try:
            # 클립 처리: 1920x1080 크기 조정, 길이 제한
            (
                ffmpeg
                .input(input_path, t=clip_duration)
                .filter('scale', 1920, 1080, force_original_aspect_ratio='decrease')
                .filter('pad', 1920, 1080, '(ow-iw)/2', '(oh-ih)/2')
                .output(output_path, vcodec='libx264', preset='medium', crf=23, an=None)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            
            processed_clips.append(output_path)
            print(f"   [{i}/{len(downloaded_files)}] Processed: {clip_duration:.1f}s")
            
        except ffmpeg.Error as e:
            print(f"   ⚠️ Processing failed for clip {i}")
            continue
    
    if len(processed_clips) < 8:
        print(f"\n❌ Only {len(processed_clips)} clips processed successfully")
        sys.exit(1)
    
    # Concat 파일 생성
    with open(concat_file, 'w') as f:
        for clip_path in processed_clips:
            f.write(f"file '{os.path.basename(clip_path)}'\n")
    
    print(f"\n🎬 Concatenating {len(processed_clips)} clips...")
    
    # 최종 영상 생성
    try:
        (
            ffmpeg
            .input(concat_file, format='concat', safe=0)
            .output('temp/silent_video.mp4', vcodec='libx264', preset='medium', crf=23)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        # 파일 크기 및 정보 확인
        file_size = os.path.getsize('temp/silent_video.mp4')
        probe = ffmpeg.probe('temp/silent_video.mp4')
        video_duration = float(probe['streams'][0]['duration'])
        
        print(f"\n✅ Silent video created!")
        print(f"💾 Saved to: temp/silent_video.mp4")
        print(f"📦 File size: {file_size/1024/1024:.1f} MB")
        print(f"⏱️ Duration: {video_duration:.1f}s ({video_duration/60:.1f} min)")
        print(f"🎞️ Resolution: 1920x1080")
        
    except ffmpeg.Error as e:
        print(f"❌ Video concatenation failed: {e.stderr.decode()}")
        sys.exit(1)
    
    # 정리
    print("\n🧹 Cleaning up temporary files...")
    for clip in downloaded_files:
        try:
            os.remove(clip['path'])
        except:
            pass
    
    for clip in processed_clips:
        try:
            os.remove(clip)
        except:
            pass
    
    print("✅ Cleanup completed")

if __name__ == "__main__":
    create_video()

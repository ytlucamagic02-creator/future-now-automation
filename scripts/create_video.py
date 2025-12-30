#!/usr/bin/env python3
"""
영상 생성 스크립트 (FFmpeg 전용) - 에러 로깅 강화 버전
"""

import json
import os
import sys
import subprocess
from pathlib import Path
import requests
import time

def download_video(url: str, output_path: str, max_retries=3) -> bool:
    """영상 다운로드 (재시도 로직 추가)"""
    for attempt in range(max_retries):
        try:
            print(f"      Downloading attempt {attempt + 1}/{max_retries}...", end=" ")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = Path(output_path).stat().st_size
            if file_size > 1024 * 100:  # 최소 100KB
                print(f"Success ({file_size / 1024 / 1024:.1f}MB)")
                return True
            else:
                print(f"Failed (file too small: {file_size}bytes)")
                
        except Exception as e:
            print(f"Failed ({e})")
            if attempt < max_retries - 1:
                time.sleep(2)
    
    return False

def get_video_duration(video_path: str) -> float:
    """FFmpeg로 영상 길이 가져오기"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', video_path],
            capture_output=True,
            text=True,
            check=True
        )
        duration = float(result.stdout.strip())
        print(f"      ✅ Duration: {duration:.1f}s")
        return duration
    except Exception as e:
        print(f"      ⚠️ Duration check failed: {e}")
        return 0.0

def process_video_ffmpeg(input_path: str, output_path: str, target_duration: float = 30.0) -> bool:
    """FFmpeg로 영상 처리"""
    try:
        duration = get_video_duration(input_path)
        if duration == 0:
            return False
        
        trim_duration = min(duration, target_duration)
        
        print(f"      🎬 Processing... (target: {trim_duration:.1f}s)", end=" ")
        
        result = subprocess.run([
            'ffmpeg', '-y',
            '-i', input_path,
            '-t', str(trim_duration),
            '-vf', 'scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080',
            '-r', '30',
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-an',
            output_path
        ], check=True, capture_output=True, text=True)
        
        print("Done")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Failed")
        print(f"      FFmpeg stderr: {e.stderr[:200]}")
        return False
    except Exception as e:
        print(f"Failed: {e}")
        return False

def create_concat_file(clip_paths: list, concat_file: str):
    """FFmpeg concat 파일 생성"""
    with open(concat_file, 'w') as f:
        for path in clip_paths:
            abs_path = Path(path).resolve()
            f.write(f"file '{abs_path}'\n")

def extract_video_urls(videos_data):
    """videos.json에서 영상 URL 추출"""
    print(f"\n🔍 Analyzing videos.json:")
    print(f"   Type: {type(videos_data)}")
    
    video_urls = []
    
    # List 형식
    if isinstance(videos_data, list):
        print(f"   Format: list (length: {len(videos_data)})")
        
        for i, video in enumerate(videos_data):
            if not isinstance(video, dict):
                continue
            
            if "url" in video and "width" in video:
                url = video["url"]
                width = video["width"]
                
                if width >= 1920 and url:
                    video_urls.append(url)
                    print(f"   ✅ [{i}] HD video: {width}x{video.get('height', '?')}")
    
    # Dict 형식
    elif isinstance(videos_data, dict):
        print(f"   Format: dict")
        videos = videos_data.get("videos", [])
        
        for i, video in enumerate(videos):
            if "url" in video and "width" in video:
                if video["width"] >= 1920:
                    video_urls.append(video["url"])
                    print(f"   ✅ [{i}] HD video")
    
    print(f"\n   📊 Extracted URLs: {len(video_urls)}\n")
    return video_urls

def create_video():
    """메인 영상 생성"""
    print("\n" + "=" * 60)
    print("🎬 Silent video creation started")
    print("=" * 60)
    
    # temp 폴더 생성
    os.makedirs('temp', exist_ok=True)
    os.makedirs('temp/clips', exist_ok=True)
    
    videos_json = Path("temp/videos.json")
    temp_dir = Path("temp/clips")
    output_file = Path("temp/silent_video.mp4")
    
    # 1단계: 파일 존재 확인
    if not videos_json.exists():
        print(f"\n❌ CRITICAL: videos.json not found!")
        print(f"   Path: {videos_json.absolute()}")
        sys.exit(1)
    
    # 2단계: JSON 로드
    try:
        with open(videos_json, 'r', encoding='utf-8') as f:
            videos_data = json.load(f)
        print(f"✅ videos.json loaded")
    except Exception as e:
        print(f"❌ CRITICAL: videos.json load failed: {e}")
        sys.exit(1)
    
    # 3단계: URL 추출
    video_urls = extract_video_urls(videos_data)
    
    if not video_urls:
        print(f"\n❌ CRITICAL: No video URLs available!")
        sys.exit(1)
    
    # 4단계: 영상 처리 준비
    target_duration = 540  # 9분
    needed_videos = 18
    
    print(f"\n🎯 Target:")
    print(f"   Duration: {target_duration / 60:.1f} minutes")
    print(f"   Videos needed: {needed_videos}")
    print(f"   Videos found: {len(video_urls)}")
    
    # 부족하면 반복
    if len(video_urls) < needed_videos:
        repeat_count = needed_videos - len(video_urls)
        video_urls.extend(video_urls[:repeat_count])
        print(f"   Videos repeated: +{repeat_count}")
    
    video_urls = video_urls[:needed_videos]
    
    # 5단계: 영상 다운로드 + 처리
    print(f"\n📥 Video download & processing:")
    processed_clips = []
    
    for i, url in enumerate(video_urls, 1):
        print(f"\n   [{i}/{len(video_urls)}] Processing...")
        print(f"      URL: {url[:60]}...")
        
        raw_path = temp_dir / f"raw_{i}.mp4"
        if not download_video(url, str(raw_path)):
            print(f"      ⚠️ Download failed, next...")
            continue
        
        processed_path = temp_dir / f"clip_{i}.mp4"
        if process_video_ffmpeg(str(raw_path), str(processed_path)):
            processed_clips.append(str(processed_path))
            print(f"      ✅ Processing completed!")
        else:
            print(f"      ⚠️ Processing failed, next...")
        
        # 원본 삭제
        raw_path.unlink(missing_ok=True)
    
    # 6단계: 최소 영상 개수 체크
    if not processed_clips:
        print(f"\n❌ CRITICAL: No processed videos!")
        sys.exit(1)
    
    print(f"\n✅ Total {len(processed_clips)} videos processed")
    
    # 7단계: 영상 병합
    concat_file = temp_dir / "concat.txt"
    create_concat_file(processed_clips, str(concat_file))
    
    print(f"\n🔗 Merging videos...")
    try:
        subprocess.run([
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
            '-c', 'copy',
            str(output_file)
        ], check=True, capture_output=True, text=True)
        
        print(f"✅ Merge completed!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ CRITICAL: Merge failed!")
        print(f"   FFmpeg stderr: {e.stderr[:300]}")
        sys.exit(1)
    
    # 8단계: 최종 확인
    if not output_file.exists():
        print(f"\n❌ CRITICAL: Final video not created!")
        sys.exit(1)
    
    final_duration = get_video_duration(str(output_file))
    final_size = output_file.stat().st_size / (1024 * 1024)
    
    print(f"\n" + "=" * 60)
    print(f"🎉 Silent video creation completed!")
    print(f"=" * 60)
    print(f"   📁 File: {output_file}")
    print(f"   📊 Size: {final_size:.1f} MB")
    print(f"   ⏱️  Duration: {final_duration / 60:.1f} minutes")
    print(f"   🎬 Clips: {len(processed_clips)}")
    print(f"   🔇 Audio: None (will be merged in next step)")
    print("=" * 60)
    
    # 정리
    concat_file.unlink(missing_ok=True)
    for clip in processed_clips:
        Path(clip).unlink(missing_ok=True)

if __name__ == "__main__":
    try:
        create_video()
    except KeyboardInterrupt:
        print("\n\n⚠️ User interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

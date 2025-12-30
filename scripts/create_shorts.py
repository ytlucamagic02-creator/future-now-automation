#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
쇼츠 영상 3개 생성 (9:16 세로 포맷)
"""

import os
import sys
import json
import ffmpeg

def create_shorts():
    """메인 영상에서 쇼츠 3개 추출 및 생성"""
    
    print("📱 Creating shorts videos (9:16 format)...")
    
    # 세그먼트 정보 읽기
    try:
        with open("temp/shorts_segments.json", "r") as f:
            data = json.load(f)
            segments = data['segments']
    except FileNotFoundError:
        print("❌ Segments file not found!")
        sys.exit(1)
    
    # 메인 영상 확인
    main_video = "temp/final_video.mp4"
    if not os.path.exists(main_video):
        print(f"❌ Main video not found: {main_video}")
        sys.exit(1)
    
    print(f"🎬 Source: {main_video}")
    print(f"📊 Creating {len(segments)} shorts...\n")
    
    # 각 세그먼트를 쇼츠로 변환
    created_shorts = []
    
    for segment in segments:
        short_id = segment['id']
        start_time = segment['start']
        duration = segment['duration']
        output_path = f"temp/short_{short_id}.mp4"
        
        print(f"[{short_id}/3] {segment['title']}")
        print(f"   Time: {start_time:.1f}s, Duration: {duration:.1f}s")
        
        try:
            # 영상 추출 및 9:16 변환
            (
                ffmpeg
                .input(main_video, ss=start_time, t=duration)
                .filter('scale', 1080, 1920, force_original_aspect_ratio='increase')
                .filter('crop', 1080, 1920)
                .output(
                    output_path,
                    vcodec='libx264',
                    preset='medium',
                    crf=23,
                    acodec='aac',
                    audio_bitrate='128k'
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            
            # 확인
            file_size = os.path.getsize(output_path)
            probe = ffmpeg.probe(output_path)
            actual_duration = float(probe['streams'][0]['duration'])
            
            print(f"   ✅ Created: {file_size/1024:.0f} KB, {actual_duration:.1f}s")
            
            created_shorts.append({
                'id': short_id,
                'path': output_path,
                'title': segment['title'],
                'duration': actual_duration
            })
            
        except ffmpeg.Error as e:
            print(f"   ❌ Failed: {e.stderr.decode()}")
            continue
    
    if len(created_shorts) == 0:
        print("\n❌ No shorts created!")
        sys.exit(1)
    
    # 결과 저장
    with open("temp/created_shorts.json", "w") as f:
        json.dump({'shorts': created_shorts}, f, indent=2)
    
    print(f"\n✅ Shorts creation completed!")
    print(f"📊 Created {len(created_shorts)}/3 shorts")
    print(f"💾 Saved to: temp/short_1.mp4, short_2.mp4, short_3.mp4")

if __name__ == "__main__":
    create_shorts()

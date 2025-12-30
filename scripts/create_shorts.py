import os
import json
import subprocess
from pathlib import Path

# temp 폴더 생성
os.makedirs('temp', exist_ok=True)

def create_srt_file(text, duration, output_path):
    """Create SRT subtitle file with automatic word grouping (5 words per subtitle)"""
    
    words = text.split()
    subtitles = []
    
    # Group words (5 words per subtitle)
    word_groups = [words[i:i+5] for i in range(0, len(words), 5)]
    
    # Calculate timing
    time_per_group = duration / len(word_groups)
    
    for i, group in enumerate(word_groups):
        start_time = i * time_per_group
        end_time = (i + 1) * time_per_group
        
        # Format time as SRT (HH:MM:SS,mmm)
        start_str = format_srt_time(start_time)
        end_str = format_srt_time(end_time)
        
        subtitle_text = ' '.join(group)
        
        subtitles.append(f"{i+1}\n{start_str} --> {end_str}\n{subtitle_text}\n")
    
    # Write SRT file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(subtitles))
    
    print(f"   ✅ Created SRT: {len(word_groups)} subtitles")

def format_srt_time(seconds):
    """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def create_shorts():
    """Create 3 vertical shorts with subtitles from the main video"""
    
    print("🎬 Creating YouTube Shorts...")
    
    # Load shorts data
    with open('temp/shorts_segments.json', 'r', encoding='utf-8') as f:
        segments = json.load(f)
    
    # Input video
    input_video = 'temp/final_video.mp4'
    
    if not os.path.exists(input_video):
        print(f"❌ Error: {input_video} not found!")
        return
    
    shorts = segments['shorts']
    
    if len(shorts) < 3:
        print(f"❌ Error: Expected 3 shorts, found {len(shorts)}")
        return
    
    print(f"📊 Processing {len(shorts)} shorts...")
    
    for i, short in enumerate(shorts[:3], 1):  # Process exactly 3 shorts
        print(f"\n📱 Short #{i}: {short['title']}")
        
        # Calculate duration
        script_text = short['script']
        word_count = len(script_text.split())
        duration = max(30, min(60, (word_count / 150) * 60))  # 30-60 seconds
        
        print(f"   📝 Words: {word_count}")
        print(f"   ⏱️ Duration: {duration:.1f}s")
        
        # Get start time
        start_time = short.get('estimated_start_time', 0)
        
        output_file = f'temp/short_{i}.mp4'
        srt_file = f'temp/short_{i}.srt'
        temp_file = f'temp/short_{i}_temp.mp4'
        
        # Step 1: Create SRT subtitle file
        create_srt_file(script_text, duration, srt_file)
        
        # Step 2: Extract and crop to vertical (1080x1920)
        print(f"   🎥 Extracting clip...")
        
        crop_cmd = [
            'ffmpeg', '-y',
            '-ss', str(start_time),
            '-i', input_video,
            '-t', str(duration),
            '-vf', 'crop=ih*9/16:ih,scale=1080:1920',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '128k',
            temp_file
        ]
        
        try:
            subprocess.run(crop_cmd, check=True, capture_output=True)
            print(f"   ✅ Clip extracted")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Crop failed: {e.stderr.decode()}")
            continue
        
        # Step 3: Add subtitles with styling
        print(f"   💬 Adding subtitles...")
        
        subtitle_cmd = [
            'ffmpeg', '-y',
            '-i', temp_file,
            '-vf', (
                f"subtitles={srt_file}:force_style='"
                "FontName=Arial Black,"
                "FontSize=28,"
                "Bold=1,"
                "PrimaryColour=&HFFFFFF&,"
                "OutlineColour=&H000000&,"
                "Outline=3,"
                "Alignment=10,"
                "MarginV=180'"
            ),
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-c:a', 'copy',
            output_file
        ]
        
        try:
            subprocess.run(subtitle_cmd, check=True, capture_output=True)
            print(f"   ✅ Subtitles added")
            
            # Clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)
                
        except subprocess.CalledProcessError as e:
            print(f"   ⚠️ Subtitle overlay failed, using video without subtitles")
            # Fallback: use temp file as final
            if os.path.exists(temp_file):
                os.rename(temp_file, output_file)
        
        # Verify output
        if os.path.exists(output_file):
            size_mb = os.path.getsize(output_file) / (1024 * 1024)
            print(f"   ✅ Short #{i} created: {size_mb:.1f} MB")
        else:
            print(f"   ❌ Failed to create short #{i}")
    
    print("\n✅ All shorts created!")
    print("\n📂 Output files:")
    for i in range(1, 4):
        short_file = f'temp/short_{i}.mp4'
        if os.path.exists(short_file):
            print(f"   • {short_file}")

if __name__ == '__main__':
    create_shorts()

#!/usr/bin/env python3
"""
Video Compression Script
Compresses all videos in src/videos directory recursively and replaces original files.
Uses FFmpeg for compression with H.264 codec and optimized settings.
"""

import os
import subprocess
import sys
from pathlib import Path
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def check_ffmpeg():
    """Check if FFmpeg is installed and available."""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_video_files(directory):
    """Recursively find all video files in the directory."""
    video_extensions = {'.mp4', '.mov', '.webm', '.avi', '.mkv', '.flv', '.wmv'}
    video_files = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if Path(file).suffix.lower() in video_extensions:
                video_files.append(os.path.join(root, file))
    
    return video_files

def get_video_info(file_path):
    """Get video file information using FFmpeg."""
    try:
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', '-show_streams', file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return None

def compress_video(input_path, output_path, quality='medium', crf=23):
    """
    Compress a video file using FFmpeg.
    
    Args:
        input_path: Path to input video file
        output_path: Path to output compressed video file
        quality: Quality preset ('low', 'medium', 'high')
        crf: Constant Rate Factor (23-32 for aggressive compression, higher = more compression)
    """
    # Quality presets - More aggressive compression
    quality_settings = {
        'low': {'crf': 32, 'preset': 'veryfast'},
        'medium': {'crf': 28, 'preset': 'fast'},
        'high': {'crf': 23, 'preset': 'medium'}
    }
    
    settings = quality_settings.get(quality, quality_settings['medium'])
    
    # FFmpeg command for compression - More aggressive settings
    cmd = [
        'ffmpeg', '-i', input_path,
        '-c:v', 'libx264',           # H.264 codec
        '-crf', str(settings['crf']), # Constant Rate Factor
        '-preset', settings['preset'], # Encoding preset
        '-c:a', 'aac',               # Audio codec
        '-b:a', '96k',               # Lower audio bitrate for more compression
        '-movflags', '+faststart',   # Optimize for web streaming
        '-maxrate', '2M',            # Maximum bitrate limit
        '-bufsize', '4M',            # Buffer size for rate limiting
        '-y',                        # Overwrite output file
        output_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True, None
    except subprocess.CalledProcessError as e:
        return False, f"FFmpeg error: {e.stderr}"

def get_file_size(file_path):
    """Get file size in bytes."""
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0

def format_size(size_bytes):
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def process_video_file(file_path, quality='medium', dry_run=False):
    """Process a single video file."""
    try:
        original_size = get_file_size(file_path)
        if original_size == 0:
            return False, f"Could not get file size for {file_path}"
        
        print(f"Processing: {file_path} ({format_size(original_size)})")
        
        if dry_run:
            print(f"  [DRY RUN] Would compress: {file_path}")
            return True, "Dry run completed"
        
        # Create temporary output path with proper extension
        file_path_obj = Path(file_path)
        temp_output = str(file_path_obj.parent / f"{file_path_obj.stem}_temp{file_path_obj.suffix}")
        
        # Compress the video
        success, error = compress_video(file_path, temp_output, quality)
        
        if not success:
            return False, error
        
        # Check if compression was successful and file is smaller
        compressed_size = get_file_size(temp_output)
        
        if compressed_size == 0:
            os.remove(temp_output)
            return False, "Compressed file is empty or could not be created"
        
        # Calculate compression ratio
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        if compressed_size >= original_size:
            print(f"  Warning: Compressed file is larger ({format_size(compressed_size)}) than original")
            print(f"  Keeping original file")
            os.remove(temp_output)
            return True, "Compressed file was larger, keeping original"
        
        # Replace original with compressed version
        os.remove(file_path)
        os.rename(temp_output, file_path)
        
        print(f"  ✓ Compressed: {format_size(original_size)} → {format_size(compressed_size)} ({compression_ratio:.1f}% reduction)")
        
        return True, f"Successfully compressed with {compression_ratio:.1f}% reduction"
        
    except Exception as e:
        return False, f"Error processing {file_path}: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description='Compress videos in src/videos directory')
    parser.add_argument('--quality', choices=['low', 'medium', 'high'], default='low',
                       help='Compression quality (default: medium)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without actually compressing')
    parser.add_argument('--max-workers', type=int, default=4,
                       help='Maximum number of parallel workers (default: 4)')
    parser.add_argument('--directory', default='src/videos',
                       help='Directory to process (default: src/videos)')
    
    args = parser.parse_args()
    
    # Check if FFmpeg is available
    if not check_ffmpeg():
        print("Error: FFmpeg is not installed or not found in PATH")
        print("Please install FFmpeg: https://ffmpeg.org/download.html")
        sys.exit(1)
    
    # Check if directory exists
    if not os.path.exists(args.directory):
        print(f"Error: Directory '{args.directory}' does not exist")
        sys.exit(1)
    
    # Find all video files
    print(f"Scanning for video files in {args.directory}...")
    video_files = get_video_files(args.directory)
    
    if not video_files:
        print("No video files found.")
        return
    
    print(f"Found {len(video_files)} video files")
    
    if args.dry_run:
        print("\n=== DRY RUN MODE ===")
        print("No files will be modified. Use --dry-run to see what would be done.\n")
    
    # Process files
    successful = 0
    failed = 0
    start_time = time.time()
    
    if args.max_workers == 1:
        # Sequential processing
        for file_path in video_files:
            success, message = process_video_file(file_path, args.quality, args.dry_run)
            if success:
                successful += 1
            else:
                failed += 1
                print(f"  ✗ Failed: {message}")
    else:
        # Parallel processing
        with ThreadPoolExecutor(max_workers=args.max_workers) as executor:
            future_to_file = {
                executor.submit(process_video_file, file_path, args.quality, args.dry_run): file_path
                for file_path in video_files
            }
            
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    success, message = future.result()
                    if success:
                        successful += 1
                    else:
                        failed += 1
                        print(f"  ✗ Failed: {message}")
                except Exception as e:
                    failed += 1
                    print(f"  ✗ Exception processing {file_path}: {str(e)}")
    
    # Summary
    elapsed_time = time.time() - start_time
    print(f"\n=== SUMMARY ===")
    print(f"Total files: {len(video_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    
    if args.dry_run:
        print("\nThis was a dry run. Run without --dry-run to actually compress the videos.")

if __name__ == "__main__":
    main() 
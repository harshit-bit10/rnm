import os
import subprocess
import logging
from PIL import Image  # Make sure to install Pillow for image processing
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import re

# Set up logging
logger = logging.getLogger(__name__)

# Metadata to be added
metadata_text = "SharkToonsIndia"

def sanitize_filename(filename):
    # Remove invalid characters and trim whitespace
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)  # Remove invalid characters
    sanitized = sanitized.strip()  # Trim whitespace
    return sanitized

async def add_metadata(file_path, new_caption):
    # Use os.path.splitext to split the file path into root and extension
    _, input_extension = os.path.splitext(os.path.basename(file_path))

    # Sanitize the new_caption to create a valid filename
    sanitized_caption = sanitize_filename(new_caption)
    
    # Remove any file extension from the sanitized_caption
    sanitized_caption = os.path.splitext(sanitized_caption)[0]

    # Append the input file's extension to the sanitized caption
    output_file = f"{sanitized_caption}{input_extension}"  # Use the input file's extension
    of_name = f"{sanitized_caption}{input_extension}"  # Use the input file's extension

    cmd = [
        'ffmpeg', '-y', '-err_detect', 'ignore_err', '-i', file_path, '-c', 'copy',
        '-map', '0', '-c:s', 'copy', '-c:a', 'copy', '-c:v', 'copy',
        '-metadata:s:s', f'title={metadata_text}',
        '-metadata:s:a', f'title={metadata_text}',
        '-metadata:s:v', f'title={metadata_text}',
        '-metadata', f'title={metadata_text} - {of_name}',
        '-metadata', 'copyright=Ripped And Encoded By -- SharkToonsIndia --',
        '-metadata', 'Copyright=Ripped And Encoded By -- SharkToonsIndia --',
        '-metadata', 'COPYRIGHT=Ripped And Encoded By -- SharkToonsIndia --',
        '-metadata', f'description=This File Is Downloaded From "@SharkToonsIndia " so Please Join Our Channels and Support Us We Need Your Support  ~ {metadata_text}',
        '-metadata', f'Description=This File Is Downloaded From "@SharkToonsIndia " so Please Join Our Channels and Support Us We Need Your Support  ~ {metadata_text}',
        '-metadata', f'license=© @SharkToonsIndia - All Rights Reserved. No reuploading or copying. DMCA Protected. Any unauthorized distribution, reproduction, or modification is a violation of DMCA and copyright laws.',
        '-metadata', f'LICENSE=© @SharkToonsIndia - All Rights Reserved. No reuploading or copying. DMCA Protected. Any unauthorized distribution, reproduction, or modification is a violation of DMCA and copyright laws.',
        '-metadata', f'License=© @SharkToonsIndia - All Rights Reserved. No reuploading or copying. DMCA Protected. Any unauthorized distribution, reproduction, or modification is a violation of DMCA and copyright laws.',
        '-metadata', f'author={metadata_text}',
        '-metadata', f'summary=This File Is Downloaded From "@SharkToonsIndia " so Please Join Our Channels and Support Us We Need Your Support  ~ {metadata_text}',
        '-metadata', f'comment=Ripped And Encoded By -- {metadata_text} --',
        '-metadata', f'Comment=Ripped And Encoded By -- {metadata_text} --',
        '-metadata', f'artist={metadata_text}',
        '-metadata', f'album={metadata_text}',
        '-metadata', f'genre={metadata_text}',
        '-metadata', f'Genre={metadata_text}',
        '-metadata', f'GENRE={metadata_text}',
        '-metadata', f'date=',
        '-metadata', f'creation_time=',
        '-metadata', f'language=',
        '-metadata', f'publisher={metadata_text}',
        '-metadata', f'encoder=Encoded By {metadata_text}',
        '-metadata', f'SUMMARY=This File Is Downloaded From "@SharkToonsIndia " so Please Join Our Channels and Support Us We Need Your Support  ~ {metadata_text}',
        '-metadata', f'Summary=This File Is Downloaded From "@SharkToonsIndia " so Please Join Our Channels and Support Us We Need Your Support  ~ {metadata_text}',
        '-metadata', f'AUTHOR={metadata_text}',
        '-metadata', f'WEBSITE=Just Join Our Telegram Channel https://t.me/SharkToonsIndia, there you will get all details regarding our website',
        '-metadata', f'COMMENT=Ripped And Encoded By -- {metadata_text} -- ',
        '-metadata', f'ENCODER=Encoded By {metadata_text}',
        '-metadata', f'Encoder=Encoded By {metadata_text}',
        '-metadata', f'FILENAME=',
        '-metadata', f'MIMETYPE=',
        '-metadata', f'PURL=',
        '-metadata', f'ALBUM={metadata_text}',
        '-metadata', f'CHANNEL=SharkToonsIndia',
        '-metadata', f'Channel=SharkToonsIndia',
        '-metadata', f'channel=SharkToonsIndia',
        '-metadata', f'encodedby=SharkToonsIndia',
        '-metadata', f'EncodedBy=SharkToonsIndia',
        '-metadata', f'ENCODEDBY=SharkToonsIndia',
        '-metadata', f'encoded_by=SharkToonsIndia',
        '-metadata', f'Encoded_By=SharkToonsIndia',
        '-metadata', f'ENCODED_BY=SharkToonsIndia',
        '-metadata', f'encoded by=SharkToonsIndia',
        '-metadata', f'Encoded By=SharkToonsIndia',
        '-metadata', f'ENCODED BY=SharkToonsIndia',
        '-metadata', f'encoded-by=SharkToonsIndia',
        '-metadata', f'Encoded-By=SharkToonsIndia',
        '-metadata', f'ENCODED-BY=SharkToonsIndia',
        output_file
    ]

    try:
        # Execute the ffmpeg command
        subprocess.run(cmd, check=True)
        return output_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Error adding metadata: {e}")
        return None

async def extract_duration(file_path):
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', file_path
    ]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        duration = result.stdout.strip()
        return float(duration)  # Convert to float
    except Exception as e:
        logger.error(f"Error extracting duration: {e}")
        return None

def get_audio_thumbnail(file_path):
    """Extract album art from MP3 file if available."""
    try:
        audio = MP3(file_path, ID3=ID3)
        for tag in audio.tags.values():
            if isinstance(tag, APIC):
                # Save the album art to a file
                thumbnail_path = f"album_art_{os.path.basename(file_path)}.jpg"
                with open(thumbnail_path, "wb") as img_file:
                    img_file.write(tag.data)
                return thumbnail_path
    except Exception as e:
        logger.error(f"Error extracting audio thumbnail: {e}")
    return None

def check_file_size(file_path):
    """Check if the file size is greater than 5 MB."""
    return os.path.getsize(file_path) > 5 * 1024 * 1024  # 5 MB in bytes

async def get_file_duration(file_path):
    """Get the duration of the file using ffprobe."""
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1', file_path
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    duration = result.stdout.strip()
    return float(duration) if duration else None

async def split_file(file_path, max_size_mb):
    """Split the file into segments based on the maximum size with 3-second overlap."""
    file_size = os.path.getsize(file_path)
    total_duration = await get_file_duration(file_path)

    if total_duration is None:
        logger.error("Could not retrieve file duration.")
        return []

    # Calculate the number of segments
    max_size_bytes = max_size_mb * 1024 * 1024  # Convert MB to bytes
    num_segments = (file_size // max_size_bytes) + 1  # Number of segments needed

    # Calculate the duration for each segment
    segment_duration = total_duration / num_segments

    output_files = []
    start_time = 0

    # Get the original file's base name and extension
    base_name, original_extension = os.path.splitext(os.path.basename(file_path))

    for i in range(num_segments):
        # Create a new filename with the original base name and "Part-X"
        output_file = f"{base_name}_Part-{i + 1}{original_extension}"

        if i == 0:
            # First segment, no overlap
            cmd = [
                'ffmpeg', '-y', '-i', file_path, '-ss', str(start_time), '-t', str(segment_duration),
                '-c', 'copy', output_file
            ]
        else:
            # Subsequent segments, overlap 3 seconds with previous segment
            overlap_start = start_time - 3  # 3 seconds overlap
            cmd = [
                'ffmpeg', '-y', '-i', file_path, '-ss', str(overlap_start), '-t', str(segment_duration + 3),
                '-c', 'copy', output_file
            ]
        
        subprocess.run(cmd, check=True)
        output_files.append(output_file)
        start_time += segment_duration  # Update start time for the next segment

    return output_files

async def extract_thumbnail(file_path, time):
    """Extract a thumbnail from the file at the specified time."""
    thumbnail_path = f"thumbnail_{os.path.basename(file_path)}.jpg"
    cmd = [
        'ffmpeg', '-y', '-i', file_path, '-ss', str(time), '-vframes', '1', thumbnail_path
    ]
    subprocess.run(cmd, check=True)
    return thumbnail_path
   # except subprocess.CalledProcessError as e:
     #   logger.error(f"Error extracting thumbnail: {e}")
       # return None

async def process_file(file_path):
    if check_file_size(file_path):
        max_size_mb = 5  # Set the maximum size for each segment in MB
        output_files = await split_file(file_path, max_size_mb)

        thumbnails = []
        for i, output_file in enumerate(output_files):
            # Calculate the midpoint of the segment for thumbnail extraction
            segment_duration = await get_file_duration(output_file)
            thumbnail_time = segment_duration / 2  # Midpoint of the segment
            thumbnail = await extract_thumbnail(output_file, thumbnail_time)
            thumbnails.append(thumbnail)

        return output_files, thumbnails
    else:
        logger.info("File size is less than 5 MB, no need to split.")
        return None, None

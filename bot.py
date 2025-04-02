import os
import logging
from pyrogram import Client, filters
from utils import (
    sanitize_filename,
    add_metadata,
    extract_duration,
    check_file_size,
    split_file,
    extract_thumbnail,
    process_file,
    get_audio_thumbnail,
    get_file_duration  # Make sure this is included
)
from PIL import Image  # Add this line at the top of main.py

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_ID = os.environ.get("API_ID", "29234663")
API_HASH = os.environ.get("API_HASH", "94235bdf61b1b42e67b113b031db5ba5")
BOT_TOKEN = "6302807884:AAHGJbJimD2eoEWRPlws4VtASTysIr8Rzk0"  # Your Bot Token as a string

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Dump Chat ID
dump_chat_id = [-1002368843413]

# Define authorized users and groups
sudo_users = {6066102279}  # Replace with actual user IDs for PM Access
sudo_groups = {-1002337988665}  # Replace with actual group chat IDs For Group Chat Access

OWNER_ID = 6066102279

# Dictionary to keep track of user requests and file counts
user_requests = {}
user_file_count = {}
user_metadata_sent = {}
user_files = {}
user_styles = {}  # Add this line to define user_styles
c_msg = None

async def is_user_sudo(client, user_id):
    # Check if the user is in the sudo_users list
    if user_id in sudo_users:
        return True

    # Check if the user is a member of any of the sudo_groups
    for group_id in sudo_users:
        try:
            user_id = await client.user_id(user_id)
            # Allow access if the user is found in the group
            return True  # If the user is found in the group, grant access
        except Exception as e:
            print(f"Error checking group membership for group {user_id}: {e}")

    return False

    # Check if the user is a member of any of the sudo_groups
    for group_id in sudo_groups:
        try:
            chat_member = await client.get_chat_member(group_id, user_id)
            # Allow access if the user is found in the group
            return True  # If the user is found in the group, grant access
        except Exception as e:
            print(f"Error checking group membership for group {group_id}: {e}")

    return False

def sudo_only(func):
    async def wrapper(client, message):
        if not await is_user_sudo(client, message.from_user.id):
            await message.reply_text("You do not have permission to use this command.")
            return
        return await func(client, message)
    return wrapper

@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text("Welcome to SharkToonsIndia Bot! Send me an audio, video, or subtitle file, and I'll add metadata to it.")

@app.on_message(filters.command("rm"))
@sudo_only
async def rm_command(client, message):
    global user_requests, user_file_count, user_metadata_sent, user_files, user_styles, c_msg
    args = message.command[1:]  # Get command arguments

    # Initialize user data if not already done
    user_id = message.from_user.id
    if user_id not in user_requests:
        user_requests[user_id] = 0
        user_file_count[user_id] = 0
        user_metadata_sent[user_id] = False
        user_files[user_id] = []
        user_styles[user_id] = []  # Initialize a separate list for styles and replacements

    # Default to processing 1 file if no arguments are provided
    if not args:
        user_requests[user_id] = 1
        c_msg = await message.reply_text("You will now process 1 file.")
        return

    try:
        # Initialize variables
        style = None
        replacements = []  # Always initialize replacements

        # Parse arguments
        i = 0
        while i < len(args):
            if args[i] == "-i":
                count = int(args[i + 1])
                user_requests[user_id] = count
                user_file_count[user_id] = 0
                user_metadata_sent[user_id] = False
                c_msg = await message.reply_text(f"You will now process {count} {'file' if count == 1 else 'files'}.")
                i += 2  # Move past the count
            elif args[i] == "-style":
                style = args[i + 1]
                i += 2  # Move past the style
            elif args[i] == "-rep":
                old_text = args[i + 1]
                new_text = args[i + 3]  # Assuming -with is right after -rep
                replacements.append((old_text.strip('$'), new_text.strip('$')))
                i += 4  # Move past the old and new text
            else:
                i += 1  # Move to the next argument

        # Store style and replacements for later use
        user_styles[user_id].append((style, replacements))

    except (ValueError, IndexError) as e:
        print("Invalid command format. Use /rm -i<number> -style <style>.")
        logger.error(f"Error processing command: {e}")

@app.on_message(filters.audio | filters.video | filters.document)
@sudo_only
async def handle_file(client, message):
    global user_requests, user_file_count, user_metadata_sent, user_files

    # Check if the user has a pending request
    user_id = message.from_user.id
    if user_id not in user_requests or user_requests[user_id] <= 0:
        print("You need to use /rm command to set the number of files to process.")
        return

    # Increment the file count for the user
    user_file_count[user_id] += 1

    # Store the file path temporarily
    user_files[user_id].append(message)

    # Check if the user has sent the expected number of files
    if user_file_count[user_id] > user_requests[user_id]:
        print("You have sent more files than expected. Please send the correct number of files.")
        return

@app.on_message(filters.command("done"))
@sudo_only
async def done_command(client, message):
    global user_requests, user_file_count, user_files, user_styles, c_msg

    user_id = message.from_user.id

    if user_id in user_requests:
        if user_file_count[user_id] < user_requests[user_id]:
            file_word = "file" if user_file_count[user_id] == 1 else "files"
            required_word = "files"  
            s_msg = await message.reply_text(
                f"You have sent {user_file_count[user_id]} {file_word}, but you need to send {user_requests[user_id]} {required_word}. Please send the correct number of files."
            )
            return

        s_msg = await message.reply_text(
            f"All {user_file_count[user_id]} {'file' if user_file_count[user_id] == 1 else 'files'} received. ✓\n"
            f"Processing will now begin. Please be patient. ⚡"
        )
        user_metadata_sent[user_id] = True

        style, replacements = user_styles[user_id][-1] if user_styles[user_id] else (None, [])

        for msg in user_files[user_id]:
            file_path = await msg.download()
            input_file = file_path
            new_caption = msg.caption
            thumb_path = None  # Initialize thumb_path

            for old_text, new_text in replacements:
                new_caption = new_caption.replace(old_text.strip('$'), new_text.strip('$'))

            # Apply styling
            if style == "bold":
                new_caption = f"**{new_caption}**"
            elif style == "italic":
                new_caption = f"<i>{new_caption}</i>"
            elif style == "underline":
                new_caption = f"__{new_caption}__"
            elif style == "strikethrough":
                new_caption = f"~~{new_caption}~~"
            elif style == "quote":
                new_caption = f"> {new_caption}"
            elif style == "spoiler":
                new_caption = f"||{new_caption}||"
            elif style == "monospace":
                new_caption = f"`{new_caption}`"

            output_file = await add_metadata(file_path, new_caption)

            if output_file:
                if check_file_size(output_file):  # File is larger than 5 MB
                    output_files = await split_file(output_file, max_size_mb=5)
                    thumbnails = []

                    for i, split_file_name in enumerate(output_files):
                        segment_duration = await get_file_duration(split_file_name)
                        thumbnail_time = segment_duration / 2
                        thumbnail = await extract_thumbnail(split_file_name, thumbnail_time)
                        thumbnails.append(thumbnail)

                        part_caption = f"{new_caption} - Part-{i + 1}"
                        with open(split_file_name, "rb") as f:
                       #     await client.send_video(msg.chat.id, f, caption=part_caption, thumb=thumbnail, duration=segment_duration)
                            await client.send_video(msg.chat.id, f, width=1280, height=720, caption=part_caption, duration=segment_duration, thumb=thumbnail)

                    await message.reply_text(f"File split into: {output_files}\nThumbnails created: {thumbnails}")
                else:  # File is smaller than 5 MB
                    # Check for thumbnails
                    if msg.audio and msg.audio.thumbs:
                        thumb_path = await client.download_media(msg.audio.thumbs[0].file_id)
                    elif msg.video and msg.video.thumbs:
                        thumb_path = await client.download_media(msg.video.thumbs[0].file_id)
                    elif msg.document and msg.document.thumbs:
                        thumb_path = await client.download_media(msg.document.thumbs[0].file_id)

                    # If no thumbnail is available, extract one
                    if not thumb_path:
                        duration = await extract_duration(output_file)
                        if duration:
                            half_duration = duration / 2
                            thumb_path = await extract_thumbnail(output_file, half_duration)

                    duration = await extract_duration(output_file)
                    if duration is not None:
                        duration = int(duration)

                        with open(output_file , "rb") as f:
                            if msg.audio:
                                await client.send_audio(msg.chat.id, f, caption=new_caption, thumb=thumb_path, duration=duration)
                            elif msg.video:
                                await client.send_video(msg.chat.id, f, width=1280, height=720, caption=new_caption, duration=duration, thumb=thumb_path)
                            elif msg.document:
                                await client.send_document(msg.chat.id, f, thumb=thumb_path, caption=new_caption)

                        response_message = (
                            f"Your file has been processed and the metadata has been added!\n\n"
                            f"File: {os.path.basename(output_file)}\n"
                            f"Duration: {duration} seconds\n"
                            f"Thumbnail: {thumb_path if thumb_path else 'No thumbnail available'}"
                        )
                        await message.reply_text(response_message)
 
                # Reset user data after processing
                del user_requests[user_id]
                del user_file_count[user_id]
                del user_metadata_sent[user_id]
                del user_files[user_id]
                del user_styles[user_id]

                # Delete The Messages
                await s_msg.delete()
                await c_msg.delete()

                # Attempt to delete the processed file
                try:
                    os.remove(output_file)
                    os.remove(input_file)
                    if thumb_path:
                        os.remove(thumb_path)
                except OSError as e:
                    logger.error(f"Error deleting file {output_file}: {e}")
                    logger.error(f"Error deleting file {input_file}: {e}")
                    if thumb_path:
                        logger.error(f"Error deleting file {thumb_path}: {e}")

    else:
        await message.reply_text("You have not initiated a file processing request. Please use /rm to start.")



app.run()

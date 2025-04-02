import os

class Config(object):
    # API credentials
    API_ID = int(os.environ.get("API_ID", 27190467))  # Replace with your actual API ID
    API_HASH = os.environ.get("API_HASH", "ff6bc6ad2faba520f426cf04ca7f5773")  # Replace with your actual API Hash
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7240304290:AAGIhDMKJMEkP32NwnBBJPg32FO4p_5EVd0")  # Replace with your actual Bot Token

    # Authorized users
    AUTH_USERS = list(int(x) for x in os.environ.get("AUTH_USERS", "6066102279").split(" "))  # Replace with actual user IDs

    # Owner ID
    OWNER_ID = int(os.environ.get("OWNER_ID", 6066102279))  # Replace with your actual Owner ID

    # Download directory
    DOWNLOAD_DIRECTORY = os.environ.get("DOWNLOAD_DIRECTORY", "./downloads")  # Default download directory

    # Log channel ID
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002368843413"))  # Replace with your actual log channel ID

    # Optional: Add any other configuration variables you need

    # Optional: Add any other configuration variables you need
    PM_AUTH_USERS = list(int(x) for x in os.environ.get("PM_AUTH_USERS", "6066102279").split())  # Replace with actual user IDs
    CHAT_ID = int(os.environ.get("CHAT_ID", -1002337988665))  # Replace with actual group ID
    DUMP_CHAT_ID = int(os.environ.get("DUMP_CHAT_ID", -1002414124327))  # Replace with actual dump chat ID

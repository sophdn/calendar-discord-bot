import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    return {
        "ICAL_URL": os.getenv('GOOGLE_ICAL_URL'),
        "DISCORD_BOT_TOKEN": os.getenv('DISCORD_BOT_TOKEN'),
        "DISCORD_GUILD_ID": int(os.getenv('DISCORD_GUILD_ID'))
    }

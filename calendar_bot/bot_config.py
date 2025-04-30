import os
from dotenv import load_dotenv

def load_config():
    ical_url = os.getenv('GOOGLE_ICAL_URL')
    discord_bot_token = os.getenv('DISCORD_BOT_TOKEN')
    discord_guild_id = os.getenv('DISCORD_GUILD_ID')

    if not ical_url or not discord_bot_token or not discord_guild_id:
        raise KeyError("Missing one or more required environment variables")

    return {
        "ICAL_URL": ical_url.strip(),
        "DISCORD_BOT_TOKEN": discord_bot_token.strip(),
        "DISCORD_GUILD_ID": int(discord_guild_id)
    }

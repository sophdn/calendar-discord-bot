import discord
from discord.ext import tasks
from bot_config.bot_config import load_config
from google_calendar.google_calendar import fetch_google_calendar_events
from discord_sync.discord_sync import sync_events, extract_hidden_id_from_description
from custom_logger.custom_logger import get_logger

config = load_config()
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
client = discord.Client(intents=intents)
logger = get_logger()

@client.event
async def on_ready():
    logger.info(f"Logged in as {client.user}")

    guild = discord.utils.get(client.guilds, id=config["DISCORD_GUILD_ID"])
    if not guild:
        print(f"Could not find guild with ID: {config['DISCORD_GUILD_ID']}")
        await client.close()
        return

    events = fetch_google_calendar_events(config["ICAL_URL"])
    if not events:
        print("No events found.")
        await client.close()
        return

    existing_events = await guild.fetch_scheduled_events()
    existing_events_dict = {extract_hidden_id_from_description(event.description): event for event in existing_events}
    await sync_events(guild, events, existing_events_dict)
    await client.close()

client.run(config["DISCORD_BOT_TOKEN"])

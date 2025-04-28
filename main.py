import discord
from discord.ext import tasks
from config import load_config
from google_calendar import fetch_google_calendar_events
from discord_sync import sync_events

# Load configuration
config = load_config()

# Create an instance of intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    guild = discord.utils.get(client.guilds, id=config["DISCORD_GUILD_ID"])
    if not guild:
        print(f"Could not find guild with ID: {config['DISCORD_GUILD_ID']}")
        await client.close()
        return

    # Fetch events
    events = fetch_google_calendar_events(config["ICAL_URL"])
    if not events:
        print("No events found.")
        await client.close()
        return

    # Fetch existing events from Discord
    existing_events = await guild.fetch_scheduled_events()
    existing_events_dict = {(event.name, event.start_time): event for event in existing_events}

    # Sync events with Discord
    await sync_events(guild, events, existing_events_dict)

    await client.close()

# Start the bot
client.run(config["DISCORD_BOT_TOKEN"])

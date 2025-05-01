import requests
import discord
from datetime import datetime
from calendar_bot.bot_config import load_config
from calendar_bot.custom_logger import get_logger
from calendar_bot.discord_sync import sync_events, extract_hidden_id_from_description

config = load_config()
logger = get_logger()

def fetch_google_calendar_events(ical_url):
    try:
        response = requests.get(ical_url)
        response.raise_for_status()
        events = []

        feed = response.text
        if 'BEGIN:VEVENT' in feed:
            event_data = feed.split('BEGIN:VEVENT')[1:]
            for event in event_data:
                summary = event.split('SUMMARY:')[1].split('\n')[0]
                start_time = event.split('DTSTART:')[1].split('\n')[0].strip()
                end_time = event.split('DTEND:')[1].split('\n')[0].strip()
                if 'DESCRIPTION:' in event:
                    description = event.split('DESCRIPTION:')[1].split('\n')[0].strip()
                else:
                    description = ""
                uid = event.split('UID:')[1].split('\n')[0].split('@google.com')[0].strip()

                start_datetime = datetime.strptime(start_time, '%Y%m%dT%H%M%S%z')
                end_datetime = datetime.strptime(end_time, '%Y%m%dT%H%M%S%z')

                events.append({
                    'summary': summary,
                    'start': start_datetime,
                    'end': end_datetime,
                    'description': description,
                    'uid': uid
                })
        return events
    except requests.exceptions.RequestException as e:
        logger.exception(f"Error fetching calendar events: {e}")
        return []

async def run_calendar_sync(bot):
    """Core sync logic for both CLI and Discord command."""
    logger.info("Starting calendar sync...")

    if not bot.is_ready():
        logger.info("Waiting for bot to become ready...")
        await bot.wait_until_ready()

    logger.info("Bot is ready. Fetching guild...")
    guild = discord.utils.get(bot.guilds, id=config["DISCORD_GUILD_ID"])
    if not guild:
        logger.warning(f"Could not find guild with ID: {config['DISCORD_GUILD_ID']}")
        return

    logger.info(f"Found guild: {guild.name} (ID: {guild.id})")
    events = fetch_google_calendar_events(config["ICAL_URL"])
    if not events:
        logger.info("No events found in calendar.")
        return

    logger.info(f"Fetched {len(events)} events from calendar.")
    existing_events = await guild.fetch_scheduled_events()
    existing_events_dict = {
        extract_hidden_id_from_description(event.description): event
        for event in existing_events
    }

    logger.info(f"Found {len(existing_events_dict)} existing scheduled events.")
    await sync_events(guild, events, existing_events_dict)
    logger.info("Calendar sync complete.")
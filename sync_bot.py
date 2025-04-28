import os
import discord
import pytz
from discord.ext import tasks
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

# Create an instance of intents
intents = discord.Intents.default()  # Use default intents

# You can enable specific intents based on your needs:
intents.messages = True  # Enable message-related events
intents.guilds = True    # Important: enable guild-related events

# Initialize the bot client with intents
client = discord.Client(intents=intents)

# Define your Google Calendar feed URL (replace with your actual feed URL)
ICAL_URL = os.getenv('GOOGLE_ICAL_URL')
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')  # Bot token
DISCORD_GUILD_ID = int(os.getenv('DISCORD_GUILD_ID'))  # Your server ID (make sure this is an int)

# Function to fetch events from Google Calendar
def fetch_google_calendar_events():
    try:
        response = requests.get(ICAL_URL)
        response.raise_for_status()  # Check if request was successful (200 OK)
        
        events = []  # This will hold the event data
        feed = response.text
        
        if 'BEGIN:VEVENT' in feed:
            event_data = feed.split('BEGIN:VEVENT')[1:]
            for event in event_data:
                summary = event.split('SUMMARY:')[1].split('\n')[0]
                start_time = event.split('DTSTART:')[1].split('\n')[0]
                start_time = start_time.strip()
                end_time = event.split('DTEND:')[1].split('\n')[0]
                end_time = end_time.strip()
                
                # Convert the event start and end time to datetime objects
                start_datetime = datetime.strptime(start_time, '%Y%m%dT%H%M%S%z')
                end_datetime = datetime.strptime(end_time, '%Y%m%dT%H%M%S%z')

                events.append({
                    'summary': summary,
                    'start': start_datetime,
                    'end': end_datetime
                })

        return events

    except requests.exceptions.RequestException as e:
        print(f"Error fetching calendar events: {e}")
        return []

@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

    print("Bot is in the following guilds:")
    for guild in client.guilds:
        print(f"Guild: {guild.name} | ID: {guild.id}")

    guild = discord.utils.get(client.guilds, id=DISCORD_GUILD_ID)
    if not guild:
        print(f"Could not find guild with ID: {DISCORD_GUILD_ID}")
        await client.close()
        return

    events = fetch_google_calendar_events()
    if not events:
        print("No events found.")
        await client.close()
        return

    # Fetch all existing scheduled events from Discord
    existing_events = await guild.fetch_scheduled_events()
    existing_events_dict = {(event.name, event.start_time): event for event in existing_events}

    # Loop through Google Calendar events
    for event in events:
        key = (event['summary'].replace("\r", ""), event['start'])
        print("YOUR KEY")
        print(key)
        # Try to match by name + start time
        discord_event = existing_events_dict.get(key)

        if discord_event:
            # If found, check if event metadata changed (e.g., description, end time)
            if (discord_event.end_time != event['end'] or
                discord_event.description != f"Synced from Google Calendar: {event['summary']}"):

                # Update event if changed
                try:
                    await discord_event.edit(
                        end_time=event['end'],
                        description=f"Synced from Google Calendar: {event['summary']}"
                    )
                    print(f"Updated event: {discord_event.name}")
                except Exception as e:
                    print(f"Failed to update event: {e}")
            else:
                print(f"No changes needed for event: {discord_event.name}")
        else:
            # If not found, create a new event
            try:
                scheduled_event = await guild.create_scheduled_event(
                    name=event['summary'],
                    start_time=event['start'],
                    end_time=event['end'],
                    description=f"Synced from Google Calendar: {event['summary']}",
                    entity_type=discord.EntityType.external,
                    location="TBD",
                    privacy_level=discord.PrivacyLevel.guild_only
                )
                print(f"Created event: {scheduled_event.name}")
            except Exception as e:
                print(f"Failed to create event: {e}")

    await client.close()

# Start the bot using your bot token
client.run(DISCORD_BOT_TOKEN)

import discord
from discord.ext import tasks

async def sync_events(guild, events, existing_events_dict):
    for event in events:
        key = (event['summary'].replace("\r", ""), event['start'])

        # Try to match by name + start time
        discord_event = existing_events_dict.get(key)

        if discord_event:
            # If found, check if event metadata changed (e.g., description, end time)
            if (discord_event.end_time != event['end'] or
                discord_event.description != f"Synced from Google Calendar: {event['summary']}"):

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

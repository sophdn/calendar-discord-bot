import discord
from discord.ext import tasks
from custom_logger.custom_logger import get_logger

async def sync_events(guild, events, existing_events_dict):
    # Build a set of current Google Calendar UIDs
    google_uids = set(event['uid'] for event in events)
    logger = get_logger()

    for event in events:
        key = event['uid']
        discord_event = existing_events_dict.get(key)

        if discord_event:
            if (discord_event.end_time != event['end'] or discord_event.start_time != event['start'] or discord_event.name != event['summary']):
                try:
                    await discord_event.edit(
                        name=event['summary'],
                        end_time=event['end'],
                        start_time=event['start'],
                        description=append_hidden_id_to_description(event)
                    )
                    logger.info(f"Updated event: {event['uid']}")
                except Exception as e:
                    logger.info(f"Failed to update event: {e}")
            else:
                logger.info(f"No changes needed for event: {event['uid']}")
        else:
            try:
                await guild.create_scheduled_event(
                    name=event['summary'],
                    start_time=event['start'],
                    end_time=event['end'],
                    description=append_hidden_id_to_description(event),
                    entity_type=discord.EntityType.external,
                    location="TBD",
                    privacy_level=discord.PrivacyLevel.guild_only
                )
                logger.info(f"Created event: {event['uid']}")
            except Exception as e:
                logger.info(f"Failed to create event: {e}")

    # 🗑️ Delete orphaned Discord events
    for uid, discord_event in existing_events_dict.items():
        if uid not in google_uids:
            try:
                await discord_event.delete()
                logger.info(f"Deleted event not found in Google Calendar: {uid}")
            except Exception as e:
                logger.info(f"Failed to delete event {uid}: {e}")


def extract_hidden_id_from_description(description):
    lines = description.splitlines()

    for line in lines:
        if 'hidden_id:' in line:
            return line.split('hidden_id:')[1].strip()
    return None

def append_hidden_id_to_description(event):
    return f"{event['description']} - hidden_id:{event['uid']}"
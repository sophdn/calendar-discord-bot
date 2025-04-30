import discord
from discord.ext import tasks
from calendar_bot.custom_logger import get_logger

logger = get_logger()

RELEVANT_EVENT_FIELDS = {
    'name': 'summary',
    'start_time': 'start',
    'end_time': 'end',
    'description': 'description'
}

def strip_hidden_id(description):
    if not description:
        return ''
    if description.strip().startswith('- hidden_id:'):
        return ''
    return description.split(' - hidden_id:')[0].strip()

def event_needs_update(discord_event, gcal_event):
    for discord_field, gcal_field in RELEVANT_EVENT_FIELDS.items():
        discord_value = getattr(discord_event, discord_field, None)
        gcal_value = gcal_event.get(gcal_field)
        discord_value = str(discord_value).strip()
        gcal_value = str(gcal_value).strip()

        if discord_field == "description":
            discord_value = strip_hidden_id(discord_value)
            gcal_value = strip_hidden_id(gcal_value)

        if discord_value != gcal_value:
            return True
    return False


async def sync_events(guild, events, existing_events_dict):
    google_uids = set(event['uid'] for event in events)

    for event in events:
        key = event['uid']
        discord_event = existing_events_dict.get(key)

        if discord_event:
            if event_needs_update(discord_event, event):
                try:
                    await discord_event.edit(
                        name=event['summary'],
                        end_time=event['end'],
                        start_time=event['start'],
                        description=append_hidden_id_to_description(event)
                        # Add new fields here as needed
                    )
                    logger.info(f"Updated event: {event['uid']}")
                except Exception as e:
                    logger.warning(f"Failed to update event {event['uid']}: {e}")
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
                logger.warning(f"Failed to create event {event['uid']}: {e}")

    for uid, discord_event in existing_events_dict.items():
        if uid not in google_uids:
            try:
                await discord_event.delete()
                logger.info(f"Deleted event not found in Google Calendar: {uid}")
            except Exception as e:
                logger.warning(f"Failed to delete event {uid}: {e}")

def extract_hidden_id_from_description(description):
    for line in description.splitlines():
        if 'hidden_id:' in line:
            return line.split('hidden_id:')[1].strip()
    return None

def append_hidden_id_to_description(event):
    return f"{event['description']} - hidden_id:{event['uid']}"

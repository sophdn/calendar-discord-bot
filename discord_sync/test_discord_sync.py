import pytest
from unittest.mock import AsyncMock
import discord
from discord_sync.discord_sync import sync_events, append_hidden_id_to_description

@pytest.mark.asyncio
async def test_existing_event_needs_update():
    mock_guild = AsyncMock()
    mock_discord_event = AsyncMock()
    mock_discord_event.start_time = "old_start"
    mock_discord_event.end_time = "old_end"
    mock_discord_event.name = "Old Event"
    mock_discord_event.description = "Some description - hidden_id:testuid123"

    mock_existing_events_dict = {
        "testuid123": mock_discord_event
    }
    events = [{
        'summary': 'Updated Event',
        'start': 'new_start',
        'end': 'new_end',
        'description': 'Updated description',
        'uid': 'testuid123'
    }]
    
    await sync_events(mock_guild, events, mock_existing_events_dict)

    mock_discord_event.edit.assert_awaited_once_with(
        name='Updated Event',
        start_time='new_start',
        end_time='new_end',
        description=append_hidden_id_to_description(events[0])
    )

@pytest.mark.asyncio
async def test_existing_event_no_update_needed():
    mock_guild = AsyncMock()
    mock_discord_event = AsyncMock()
    mock_discord_event.start_time = "new_start"
    mock_discord_event.end_time = "new_end"
    mock_discord_event.name = "Updated Event"
    mock_discord_event.description = "Updated description - hidden_id:testuid123"

    mock_existing_events_dict = {
        "testuid123": mock_discord_event
    }
    events = [{
        'summary': 'Updated Event',
        'start': 'new_start',
        'end': 'new_end',
        'description': 'Updated description',
        'uid': 'testuid123'
    }]
    
    await sync_events(mock_guild, events, mock_existing_events_dict)

    mock_discord_event.edit.assert_not_awaited()
    mock_guild.create_scheduled_event.assert_not_called()

@pytest.mark.asyncio
async def test_create_new_event():
    mock_guild = AsyncMock()
    mock_existing_events_dict = {}
    events = [{
        'summary': 'New Event',
        'start': 'start_time',
        'end': 'end_time',
        'description': 'Brand new event',
        'uid': 'newuid456'
    }]

    await sync_events(mock_guild, events, mock_existing_events_dict)

    mock_guild.create_scheduled_event.assert_awaited_once_with(
        name='New Event',
        start_time='start_time',
        end_time='end_time',
        description=append_hidden_id_to_description(events[0]),
        entity_type=discord.EntityType.external,
        location="TBD",
        privacy_level=discord.PrivacyLevel.guild_only
    )

@pytest.mark.asyncio
async def test_edit_event_exception_handling(capfd):
    mock_guild = AsyncMock()
    mock_discord_event = AsyncMock()
    mock_discord_event.start_time = "old_start"
    mock_discord_event.end_time = "old_end"
    mock_discord_event.name = "Old Event"
    mock_discord_event.description = "old_description - hidden_id:testuid123"
    mock_discord_event.edit.side_effect = Exception("edit error")

    mock_existing_events_dict = {
        "testuid123": mock_discord_event
    }
    events = [{
        'summary': 'Updated Event',
        'start': 'new_start',
        'end': 'new_end',
        'description': 'Updated description',
        'uid': 'testuid123'
    }]
    
    await sync_events(mock_guild, events, mock_existing_events_dict)

    out, _ = capfd.readouterr()
    assert "Failed to update event" in out

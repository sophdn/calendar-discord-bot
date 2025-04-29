import pytest
from unittest.mock import AsyncMock, patch
from discord_sync.discord_sync import sync_events

@pytest.mark.asyncio
async def test_existing_event_needs_update():
    mock_guild = AsyncMock()
    mock_discord_event = AsyncMock()
    mock_discord_event.end_time = "old_end"
    mock_discord_event.description = "old_description"
    mock_existing_events_dict = {
        ("Test Event", "start_time"): mock_discord_event
    }
    events = [{
        'summary': 'Test Event',
        'start': 'start_time',
        'end': 'new_end'
    }]
    
    await sync_events(mock_guild, events, mock_existing_events_dict)

    mock_discord_event.edit.assert_awaited_once_with(
        end_time='new_end',
        description='Synced from Google Calendar: Test Event'
    )

@pytest.mark.asyncio
async def test_existing_event_no_update_needed():
    mock_guild = AsyncMock()
    mock_discord_event = AsyncMock()
    mock_discord_event.end_time = "end_time"
    mock_discord_event.description = "Synced from Google Calendar: Test Event"
    mock_existing_events_dict = {
        ("Test Event", "start_time"): mock_discord_event
    }
    events = [{
        'summary': 'Test Event',
        'start': 'start_time',
        'end': 'end_time'
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
        'end': 'end_time'
    }]

    await sync_events(mock_guild, events, mock_existing_events_dict)

    mock_guild.create_scheduled_event.assert_awaited_once()

@pytest.mark.asyncio
async def test_edit_event_exception_handling(capfd):
    mock_guild = AsyncMock()
    mock_discord_event = AsyncMock()
    mock_discord_event.end_time = "old_end"
    mock_discord_event.description = "old_description"
    mock_discord_event.edit.side_effect = Exception("edit error")
    mock_existing_events_dict = {
        ("Test Event", "start_time"): mock_discord_event
    }
    events = [{
        'summary': 'Test Event',
        'start': 'start_time',
        'end': 'new_end'
    }]

    await sync_events(mock_guild, events, mock_existing_events_dict)

    out, err = capfd.readouterr()
    assert "Failed to update event" in out

@pytest.mark.asyncio
async def test_create_event_exception_handling(capfd):
    mock_guild = AsyncMock()
    mock_guild.create_scheduled_event.side_effect = Exception("create error")
    mock_existing_events_dict = {}
    events = [{
        'summary': 'New Event',
        'start': 'start_time',
        'end': 'end_time'
    }]

    await sync_events(mock_guild, events, mock_existing_events_dict)

    out, err = capfd.readouterr()
    assert "Failed to create event" in out

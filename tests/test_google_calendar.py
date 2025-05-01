import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from calendar_bot.google_calendar import run_calendar_sync, fetch_google_calendar_events
from calendar_bot.discord_sync import append_hidden_id_to_description, extract_hidden_id_from_description

# Test parsing events
@patch('calendar_bot.google_calendar.requests.get')
def test_fetch_google_calendar_events(mock_get):
    sample_ical = """
BEGIN:VEVENT
SUMMARY:Test Event
DTSTART:20240428T120000Z
DTEND:20240428T130000Z
DESCRIPTION:This is a test event
UID:testuid123@google.com
END:VEVENT
"""
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = sample_ical

    events = fetch_google_calendar_events("fake_url")

    assert len(events) == 1
    event = events[0]
    assert event['summary'] == "Test Event"
    assert event['description'] == "This is a test event"
    assert event['uid'] == "testuid123"
    assert event['start'].year == 2024
    assert event['end'].year == 2024

# Test appending hidden ID to description
def test_append_hidden_id_to_description():
    event = {
        'description': 'This is a description',
        'uid': 'abc123'
    }
    result = append_hidden_id_to_description(event)
    assert "hidden_id:abc123" in result
    assert result.startswith('This is a description')

# Test extracting hidden ID from description
def test_extract_hidden_id_from_description():
    description = "This is a description - hidden_id:abc123"
    uid = extract_hidden_id_from_description(description)
    assert uid == "abc123"

def test_extract_hidden_id_from_description_missing():
    description = "This is a description without a hidden ID"
    uid = extract_hidden_id_from_description(description)
    assert uid is None

# Async test for run_calendar_sync
@pytest.mark.asyncio
@patch('calendar_bot.google_calendar.sync_events', new_callable=AsyncMock)
@patch('calendar_bot.google_calendar.fetch_google_calendar_events')
@patch('calendar_bot.google_calendar.discord.utils.get')
async def test_run_calendar_sync(mock_get_guild, mock_fetch_events, mock_sync_events):
    # Create a fake bot with is_ready and wait_until_ready
    mock_bot = MagicMock()
    mock_bot.is_ready.return_value = True
    mock_bot.guilds = [MagicMock(id=1234567890, name="Test Guild")]

    # Simulate the config's GUILD_ID matching the mocked guild
    from calendar_bot import google_calendar
    google_calendar.config["DISCORD_GUILD_ID"] = 1234567890

    # Create fake calendar events
    mock_event = {
        'summary': 'Event Title',
        'start': asyncio.get_event_loop().time(),
        'end': asyncio.get_event_loop().time(),
        'description': 'Description',
        'uid': 'uid123'
    }
    mock_fetch_events.return_value = [mock_event]

    # Create a fake guild with async fetch_scheduled_events
    fake_existing_event = MagicMock()
    fake_existing_event.description = "Some description with hidden_id:uid123"
    fake_guild = MagicMock()
    fake_guild.fetch_scheduled_events = AsyncMock(return_value=[fake_existing_event])
    mock_get_guild.return_value = fake_guild

    await run_calendar_sync(mock_bot)

    mock_fetch_events.assert_called_once()
    fake_guild.fetch_scheduled_events.assert_awaited_once()
    mock_sync_events.assert_awaited_once()

    # Check that sync_events got the correct values
    args, kwargs = mock_sync_events.call_args
    assert args[0] == fake_guild  # guild
    assert isinstance(args[1], list)  # events
    assert isinstance(args[2], dict)  # existing events by hidden_id

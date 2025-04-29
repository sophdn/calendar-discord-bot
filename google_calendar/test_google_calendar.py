import pytest
from unittest.mock import patch
from google_calendar.google_calendar import fetch_google_calendar_events
from discord_sync.discord_sync import append_hidden_id_to_description, extract_hidden_id_from_description

# Test parsing events
@patch('google_calendar.google_calendar.requests.get')
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

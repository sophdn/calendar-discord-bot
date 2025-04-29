import pytest
from unittest.mock import patch, MagicMock
from google_calendar.google_calendar import fetch_google_calendar_events
import requests

def test_fetch_google_calendar_events_success():
    fake_ical_data = """BEGIN:VCALENDAR
BEGIN:VEVENT
SUMMARY:Test Event
DTSTART:20240428T120000Z
DTEND:20240428T130000Z
END:VEVENT
END:VCALENDAR"""

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = fake_ical_data

    with patch('google_calendar.google_calendar.requests.get', return_value=mock_response):
        events = fetch_google_calendar_events("http://fakeurl.com/calendar.ics")
        assert len(events) == 1
        assert events[0]['summary'] == 'Test Event'
        assert events[0]['start'].isoformat() == '2024-04-28T12:00:00+00:00'
        assert events[0]['end'].isoformat() == '2024-04-28T13:00:00+00:00'

def test_fetch_google_calendar_events_network_error():
    with patch('google_calendar.google_calendar.requests.get', side_effect=requests.exceptions.RequestException):
        events = fetch_google_calendar_events("http://fakeurl.com/calendar.ics")
        assert events == []

def test_fetch_google_calendar_events_empty_feed():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "BEGIN:VCALENDAR\nEND:VCALENDAR"

    with patch('google_calendar.google_calendar.requests.get', return_value=mock_response):
        events = fetch_google_calendar_events("http://fakeurl.com/calendar.ics")
        assert events == []


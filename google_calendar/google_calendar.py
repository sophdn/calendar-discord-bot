import requests
from datetime import datetime
from custom_logger.custom_logger import get_logger

def fetch_google_calendar_events(ical_url):
    logger = get_logger()

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

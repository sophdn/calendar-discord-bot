import requests
from datetime import datetime

def fetch_google_calendar_events(ical_url):
    try:
        response = requests.get(ical_url)
        response.raise_for_status()  # Check if request was successful (200 OK)
        events = []

        feed = response.text
        if 'BEGIN:VEVENT' in feed:
            event_data = feed.split('BEGIN:VEVENT')[1:]
            for event in event_data:
                summary = event.split('SUMMARY:')[1].split('\n')[0]
                start_time = event.split('DTSTART:')[1].split('\n')[0].strip()
                end_time = event.split('DTEND:')[1].split('\n')[0].strip()

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

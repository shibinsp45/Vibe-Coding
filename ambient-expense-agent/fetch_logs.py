import google.auth
from google.cloud import logging

credentials, project = google.auth.default()
client = logging.Client(project='vibe-coding-499608', credentials=credentials)
for entry in client.list_entries(filter_='resource.type="aiplatform.googleapis.com/ReasoningEngine" AND textPayload=~"ERROR|Exception" AND timestamp >= "2026-06-19T09:02:00Z"', max_results=20):
    print(f"[{entry.timestamp}] {entry.severity}: {entry.payload}")

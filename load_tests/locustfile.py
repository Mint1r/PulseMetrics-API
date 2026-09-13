from locust import HttpUser, task, between
import uuid
API_KEY = 'aauE_-rSEadv-GzjWmSsc-o6NpChufviwMVfRTkRjwE'
PROJECT_ID = '328c4ed9-c527-4f3e-b6dc-7d552a67083c'

class EventUser(HttpUser):
    wait_time = between(0, 0.02)

    @task
    def ingest_event(self):
        self.client.post(
            "/api/v1/events",
            json={
                "project_id": PROJECT_ID,
                "api_key": API_KEY,
                "event_type": "page_view",
                "user_id": str(uuid.uuid4()),
                "session_id": str(uuid.uuid4()),
                "properties": {
                    "page": "/home"
                }
            }
        )

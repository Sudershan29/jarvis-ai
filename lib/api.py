import requests
import os

if os.getenv("ENV") != "production":
    from dotenv import load_dotenv

    load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL")
API_SECRET  = os.getenv("API_SECRET")

def get_events(user_token):
    response = requests.get(f"{BACKEND_URL}/calendars/events", headers={"Authorization": f"Bearer {user_token}"})
    if response.status_code != 200:
        return []

    return response.json().get("events", [])


def getContextForAIAssistant(user_token, startTime, endTime):
    response = requests.get(
        f"{BACKEND_URL}/ai/prepare",
        headers={"Authorization": f"Bearer {user_token}", "x-api-key": API_SECRET},
        params={"startTime": startTime, "endTime": endTime},
    )
    if response.status_code != 200:
        return [], [], []

    data = response.json()
    return data.get("events", []), data.get("routines", []), data.get("scheduling", [])

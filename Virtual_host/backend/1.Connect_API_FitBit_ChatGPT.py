import os
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
import gather_keys_oauth2 as oauth2
import fitbit
from datetime import datetime, timedelta
load_dotenv()
# ---------- CONFIG ----------
#CLIENT_ID = os.getenv('23TRFB')
#CLIENT_SECRET = os.getenv("15eeaa771aedb966c5a700d42086c64c")
#REDIRECT_URI = os.getenv("http://127.0.0.1:8080/")

CLIENT_ID = '23TRFB'
CLIENT_SECRET = '15eeaa771aedb966c5a700d42086c64c'
REDIRECT_URI = 'http://127.0.0.1:8080/'
openai_client = OpenAI(api_key="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")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- FITBIT AUTH (ONCE) ----------
server = oauth2.OAuth2Server(
    CLIENT_ID,
    CLIENT_SECRET,
    redirect_uri=REDIRECT_URI
)
server.browser_authorize()

access_token = server.fitbit.session.token["access_token"]

# ---------- HELPERS ----------
def get_latest_heart_rate():
    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
    url = 'https://api.fitbit.com/1/user/-/activities/heart/date/2026-01-23/1d/1min.json'

    #url = "https://api.fitbit.com/1/user/-/activities/heart/date/today/1d/1min.json"
    headers = {"Authorization": f"Bearer {access_token}"}

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    dataset = r.json()["activities-heart-intraday"]["dataset"]
    if not dataset:
        raise Exception("No heart rate data. Sync Fitbit app.")

    latest = dataset[-1]
    return latest["value"], latest["time"]

def get_ai_advice(hr):
    prompt = f"""
    You are a professional fitness coach.

    Current heart rate: {hr} BPM

    Give short, practical fitness advice based on this value.
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=120
    )

    return response.choices[0].message.content

# ---------- API ----------
@app.post("/coach")
def coach():
    try:
        hr, time = get_latest_heart_rate()
        advice = get_ai_advice(hr)

        # Change "advice" to "message" to match your React code
        return {
            "heart_rate": hr,
            "time": time,
            "message": advice  # <--- THIS IS THE KEY CHANGE
        }
    except Exception as e:
        return {
            "heart_rate": "N/A",
            "time": "N/A",
            "message": f"Error: {str(e)}" # Still uses "message" so React sees it
        }

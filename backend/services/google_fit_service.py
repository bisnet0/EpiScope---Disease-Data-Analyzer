import requests
import time
from datetime import datetime, timedelta
import os


def fetch_google_fit_metrics(access_token):

    end_time_ms = int(time.time() * 1000)
    start_time_ms = end_time_ms - (24 * 60 * 60 * 1000)

    url = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"
    headers = {"Authorization": f"Bearer {access_token}"}

    payload = {
        "aggregateBy": [
            {"dataTypeName": "com.google.step_count.delta"},
            {"dataTypeName": "com.google.heart_rate.bpm"},
            {"dataTypeName": "com.google.sleep.segment"},
        ],
        "bucketByTime": {"durationMillis": 86400000},
        "startTimeMillis": start_time_ms,
        "endTimeMillis": end_time_ms,
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json() if response.status_code == 200 else None


def get_google_fit_data(access_token):

    now = datetime.utcnow()
    start_time = now - timedelta(hours=24)

    start_time_ms = int(start_time.timestamp() * 1000)
    end_time_ms = int(now.timestamp() * 1000)

    url = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"
    headers = {"Authorization": f"Bearer {access_token}"}

    payload = {
        "aggregateBy": [
            {"dataTypeName": "com.google.step_count.delta"},
            {"dataTypeName": "com.google.sleep.segment"},
            {"dataTypeName": "com.google.heart_rate.bpm"},
        ],
        "bucketByTime": {"durationMillis": 86400000},
        "startTimeMillis": start_time_ms,
        "endTimeMillis": end_time_ms,
    }

    res = requests.post(url, json=payload, headers=headers)
    if res.status_code != 200:
        return None

    data = res.json()
    metrics = {"steps": 0, "sleep_minutes": 0, "resting_hr": 0}

    for bucket in data.get("bucket", []):
        for dataset in bucket.get("dataset", []):
            for point in dataset.get("point", []):
                dtype = point.get("dataTypeName")
                value = point.get("value", [{}])[0]

                if "step_count" in dtype:
                    metrics["steps"] += value.get("intVal", 0)
                elif "sleep" in dtype:
                    duration = (
                        (int(point["endTimeNanos"]) - int(point["startTimeNanos"]))
                        / 1e9
                        / 60
                    )
                    metrics["sleep_minutes"] += int(duration)
                elif "heart_rate" in dtype:
                    metrics["resting_hr"] = value.get("fpVal", 0)

    return metrics


def get_google_fit_data_expanded(access_token):

    now = datetime.now()
    start_of_day = datetime(now.year, now.month, now.day)
    start_time_ms = int(start_of_day.timestamp() * 1000)
    end_time_ms = int(now.timestamp() * 1000)

    url = "https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate"
    headers = {"Authorization": f"Bearer {access_token}"}

    payload = {
        "aggregateBy": [
            {
                "dataTypeName": "com.google.step_count.delta",
                "dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps",
            },
            {
                "dataTypeName": "com.google.sleep.segment",
                "dataSourceId": "derived:com.google.sleep.segment:com.google.android.gms:merged",
            },
            {
                "dataTypeName": "com.google.heart_rate.bpm",
                "dataSourceId": "derived:com.google.heart_rate.bpm:com.google.android.gms:merged",
            },
        ],
        "bucketByTime": {"durationMillis": 86400000},
        "startTimeMillis": start_time_ms,
        "endTimeMillis": end_time_ms,
    }
    res = requests.post(url, json=payload, headers=headers)
    if res.status_code != 200:
        return None

    data = res.json()

    metrics = {
        "steps": 0,
        "sleep_minutes": 0,
        "bpm_min": 0,
        "bpm_max": 0,
        "bpm_avg": 0,
    }

    for bucket in data.get("bucket", []):
        for dataset in bucket.get("dataset", []):
            for point in dataset.get("point", []):
                print(f"DEBUG POINT: {point}")
                dtype = point.get("dataTypeName")
                value = point.get("value", [{}])[0]

                if "step_count" in dtype:
                    metrics["steps"] += value.get("intVal", 0)
                elif "sleep" in dtype:
                    duration = (
                        (int(point["endTimeNanos"]) - int(point["startTimeNanos"]))
                        / 1e9
                        / 60
                    )
                    metrics["sleep_minutes"] += int(duration)
                elif "heart_rate" in dtype:
                    metrics["bpm_min"] = value.get("min", 0)
                    metrics["bpm_max"] = value.get("max", 0)
                    metrics["bpm_avg"] = value.get("fpVal", 0)

    return metrics


def refresh_google_token(refresh_token):
    url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": os.environ.get("GOOGLE_FIT_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_FIT_CLIENT_SECRET"),
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    res = requests.post(url, data=data)
    if res.status_code == 200:
        return res.json()
    return None

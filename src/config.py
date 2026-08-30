import requests
from datetime import datetime
from time import monotonic, sleep
from msvcrt import kbhit, getwch

INTERVAL = 2

BASE_URL = "https://cf.nascar.com"

SERIES = {
    1: "Cup Series",
    2: "O'Reilly Auto Parts Series",
    3: "Craftsman Truck Series",
    999: "Whelen Modified Tour"
}

FLAG_STATE = {
    1: "\033[30;42m GREEN \033[0m",
    2: "\033[30;43m YELLOW \033[0m",
    3: "\033[30;41m RED? \033[0m",
    4: "\033[30;47mC\033[37;40mH\033[30;47mE\033[37;40mC\033[30;47mK\033[37;40mE\033[30;47mD\033[0m",
    8: "PRE-RACE",
    9: "COMPLETED"
}

try:
    response = requests.get(
        f"{BASE_URL}/live/feeds/live-feed.json",
        timeout=10
    )
    response.raise_for_status()

    data = response.json()

    series_id = data["series_id"]
    race_id = data["race_id"]

except (requests.RequestException, KeyError):
    race_id = 5623
    series_id = 1

year = datetime.now().year

FEEDS = {
    "live-feed":
        f"{BASE_URL}/live/feeds/live-feed.json",

    "live-pit-data":
        f"{BASE_URL}/cacher/live/series_{series_id}/{race_id}/live-pit-data.json",

    "live-points":
        f"{BASE_URL}/live/feeds/series_{series_id}/{race_id}/live_points.json",

    "lap-times":
        f"{BASE_URL}/cacher/live/series_{series_id}/{race_id}/lap-times.json",

    "lap-notes":
        f"{BASE_URL}/cacher/{year}/{series_id}/{race_id}/lap-notes.json",

    "weekend-feed":
        f"{BASE_URL}/cacher/{year}/{series_id}/{race_id}/weekend-feed.json",

    "points-feed":
        f"{BASE_URL}/cacher/{year}/{series_id}/points-feed.json",

    "owners-points":
        f"{BASE_URL}/cacher/{year}/{series_id}/final/{series_id}-owners-points.json",

    "loop-stats":
        f"{BASE_URL}/loopstats/prod/{year}/{series_id}/{race_id}.json",

    "schedule":
        f"{BASE_URL}/cacher/{year}/race_list_basic.json",

    "live-ops":
        f"{BASE_URL}/live-ops/live-ops.json",

    "audio-mapping":
        f"{BASE_URL}/config/audio/audio_mapping_{series_id}_3.json",

    "runs":
        f"{BASE_URL}/cacher/{year}/{series_id}/{race_id}/runs.json",

    "ncs":
        f"{BASE_URL}/racing-insights/raw-feed/{race_id}-NCS.json"
}

def sleeper(duration):
    end = monotonic() + max(0, duration)

    while monotonic() < end:
        if kbhit() and getwch() == "\r":
            return True

        sleep(0.05)

    return False

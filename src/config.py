import requests
from datetime import datetime
from time import monotonic, sleep
from msvcrt import kbhit, getwch

#Enter      \r
#Escape     \x1b
#Backspace  \b
relaunch = "\r"

interval = 2

try:
    response = requests.get("https://cf.nascar.com/live/feeds/live-feed.json", timeout=10)
    response.raise_for_status()
    data = response.json()
    series_id = data["series_id"]
    race_id = data["race_id"]
    run_type = data["run_type"]
except:
    race_id = 5627
    series_id = 1

year = datetime.now().year

feeds = {
    "live-feed": f"https://cf.nascar.com/live/feeds/live-feed.json",
    "live-pit-data": f"https://cf.nascar.com/cacher/live/series_{series_id}/{race_id}/live-pit-data.json",
    "live-points": f"https://cf.nascar.com/live/feeds/series_{series_id}/{race_id}/live_points.json",
    "lap-times": f"https://cf.nascar.com/cacher/live/series_{series_id}/{race_id}/lap-times.json",
    "lap-notes": f"https://cf.nascar.com/cacher/{year}/{series_id}/{race_id}/lap-notes.json",
    "weekend-feed": f"https://cf.nascar.com/cacher/{year}/{series_id}/{race_id}/weekend-feed.json",
    "points-feed": f"https://cf.nascar.com/cacher/{year}/{series_id}/points-feed.json",
    "owners-points": f"https://cf.nascar.com/cacher/{year}/{series_id}/final/{series_id}-owners-points.json",
    "loop-stats": f"https://cf.nascar.com/loopstats/prod/{year}/{series_id}/{race_id}.json",
    "schedule": f"https://cf.nascar.com/cacher/{year}/race_list_basic.json",
    "live-ops": f"https://cf.nascar.com/live-ops/live-ops.json",
    "audio-mapping": f"https://cf.nascar.com/config/audio/audio_mapping_{series_id}_3.json",
    "runs": f"https://cf.nascar.com/cacher/{year}/{series_id}/{race_id}/runs.json",
    "ncs": f"https://cf.nascar.com/racing-insights/raw-feed/{race_id}-NCS.json"
}

def sleeper(duration):
    end = monotonic() + duration
    while monotonic() < end:
        if kbhit() and getwch() == relaunch:
            return True
        sleep(0.05)
    return False
import json
import requests
from time import monotonic
from subprocess import run
from threading import Thread, Event

from src import config, replay


def main(live, race_id, lap_option):
    stop_event = Event()
    ready_event = Event()

    if not live:
        start_replay(race_id, lap_option, stop_event, ready_event)

        ready_event.wait()

    next_check = monotonic()
    previous_feed = ""
    etag = ""
    session = requests.Session()

    while True:
        if live:
            live_feed, etag = get_live_feed(session, etag)

            if live_feed is None:
                next_check += config.INTERVAL

                if config.sleeper(next_check - monotonic()):
                    return

                continue

        else:
            live_feed = get_replay_feed(race_id)

            if live_feed == previous_feed:
                next_check += config.INTERVAL

                if config.sleeper(next_check - monotonic()):
                    return

                continue

            previous_feed = live_feed

        print_leaderboard(live_feed)

        next_check += config.INTERVAL

        if config.sleeper(next_check - monotonic()):
            stop_event.set()
            return


def start_replay(race_id, lap_option, stop_event, ready_event):
    replay_thread = Thread(
        target=replay.main,
        args=(race_id, lap_option, stop_event, ready_event),
        daemon=True
    )

    replay_thread.start()


def get_live_feed(session, etag):
    try:
        response = session.get(
            config.FEEDS["live-feed"],
            headers={"If-None-Match": etag},
            timeout=10
        )

        if response.status_code == 304:
            return None, etag

        response.raise_for_status()

        return response.json(), response.headers.get("ETag")

    except requests.RequestException as e:
        print(f"failed: {e}")
        return None, etag


def get_replay_feed(race_id):
    with open(
        f"replay/{race_id}/live-feed/live-feed.json"
    ) as file:
        return json.load(file)


def print_leaderboard(live_feed):
    print_header(live_feed)
    print_table_header()

    for vehicle in live_feed["vehicles"]:
        print_vehicle(vehicle)


def print_header(live_feed):
    division = config.SERIES[live_feed["series_id"]]

    hours, remainder = divmod(live_feed["elapsed_time"], 3600)
    minutes, seconds = divmod(remainder, 60)

    percent = (live_feed["lap_number"] / live_feed["laps_in_race"])

    progress = int(percent * 30)

    run("cls", shell=True)

    print(
        f"\n\033[1;33m/\033[1;31m//\033[1;34m//"
        f"\033[1;37mNASCAR\033[0m {division} - "
        f"{live_feed['run_name']} at "
        f"{live_feed['track_name']}\n"
    )

    print(
        f"{'█' * progress}"
        f"{'░' * (30 - progress)} "
        f"{percent:.0%} "
        f"{live_feed['lap_number']}/"
        f"{live_feed['laps_in_race']}"
        f"  {config.FLAG_STATE[live_feed['flag_state']]}  "
        f"{hours}:{minutes:02}:{seconds:02}\n"
    )


def print_table_header():
    print(
        f"{'POS':<5}"
        f"{'NUM':<5}"
        f"{'NAME':<15}"
        f"{' DELTA':<8}"
        f"{' LAST':<8}"
        f"{'PIT':<5}"
        f"{'   BEST':<12}"
        f"{'SPONSOR'}\n"
    )


def print_vehicle(vehicle):
    delta_display = format_delta(vehicle)

    color = "\033[90m" if vehicle["status"] != 1 else ""

    name = (
        vehicle["driver"]["last_name"]
        .replace("(i)", "")
        .replace("#", "")
        .replace("*", "")
        .strip()
    )

    pit_lap = max(
        (
            pit["pit_in_leader_lap"]
            for pit in vehicle["pit_stops"]
        ),
        default=""
    )

    print(
        f"{color}"
        f"P{vehicle['running_position']:<4}"
        f"#{vehicle['vehicle_number']:<4}"
        f"{name:<15}"
        f"{delta_display:<8}"
        f"{vehicle['last_lap_time']:<8.3f}"
        f"{pit_lap:<5}"
        f"{vehicle['best_lap_time']:<6.3f}|"
        f"{vehicle['best_lap']:<5}"
        f"{vehicle['sponsor_name']:<8}"
        f"\033[0m"
    )


def format_delta(vehicle):
    if vehicle["running_position"] == 1:
        return ""

    if vehicle["delta"] < 10:
        delta = f"{vehicle['delta']:.3f}"

        if vehicle["delta"] < 0:
            delta = f"{vehicle['delta']:.0f}"

        return f" {delta}"

    return f"{vehicle['delta']:.3f}"
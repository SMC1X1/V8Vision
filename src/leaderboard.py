import requests
import json
from time import monotonic, sleep
from subprocess import run
from threading import Thread, Event
from src import config, replay

def main(live, race_id, lap_option):
    series_id = {
        1: "Cup Series",
        2: "O'Reily Auto Parts Series",
        3: "Craftsman Truck Series",
        999: "Whelen Modified Tour"
    }
    flag_state = {
        1: "\033[30;42m GREEN \033[0m",
        2: "\033[30;43m YELLOW \033[0m",
        3: "\033[30;41m RED? \033[0m",
        4: "\033[30;47mC\033[37;40mH\033[30;47mE\033[37;40mC\033[30;47mK\033[37;40mE\033[30;47mR\033[37;40mE\033[30;47mD\033[0m",
        8: "PRE-RACE",
        9: "COMPLETED"
    }

    stop_event = Event()
    if not live:
        replay_thread = Thread(
            target=replay.main,
            args=(stop_event, race_id, lap_option),
            daemon=True
        )
        replay_thread.start()
        sleep(1)


    next_check = monotonic()
    previous_feed = ""
    etag = ""
    session = requests.Session()

    while True:
        if live:
            try:
                response = session.get(f"{config.feeds["live-feed"]}", headers={"If-None-Match": etag}, timeout=10)
                if response.status_code == 304:
                    next_check += 1
                    if config.sleeper(max(0, next_check - monotonic())):
                        return
                    continue
                response.raise_for_status()
                live_feed = response.json()
                etag = response.headers.get("ETag")
            except requests.RequestException as e:
                print(f"failed: {e}")
        else:
            with open(f"replay/{race_id}/live-feed/live-feed.json") as file:
                live_feed = json.load(file)
            if live_feed == previous_feed:
                next_check += 1
                if config.sleeper(max(0, next_check - monotonic())):
                    return
                continue
            previous_feed = live_feed

        division = series_id[live_feed["series_id"]]
        
        hours, remainder = divmod(live_feed["elapsed_time"], 3600)
        minutes, seconds = divmod(remainder, 60)

        percent = live_feed["lap_number"] / live_feed["laps_in_race"]
        progress = int(percent * 30)

        run("cls", shell=True)
        print(
            f"\n\033[1;33m/\033[1;31m//\033[1;34m//\033[1;37mNASCAR\033[0m {division} - "
            f"{live_feed["run_name"]} at {live_feed["track_name"]}\n"
        )
        print(
            f"{"█" * progress}{"░" * (30 - progress)} {percent:.0%} "
            f"{live_feed["lap_number"]}/{live_feed["laps_in_race"]}"
            f"  {flag_state[live_feed["flag_state"]]}  "
            f"{hours}:{minutes:02}:{seconds:02}\n"
        )

        print(f"{"POS":<5}{"NUM":<5}{"NAME":<15}{" DELTA":<8}{" LAST":<8}{"PIT":<5}{"   BEST":<12}{"SPONSOR"}\n")

        for vehicle in live_feed["vehicles"]:

            if vehicle["running_position"] == 1:
                delta_display = ""
            elif vehicle["delta"] < 10:
                delta_display = f" {vehicle["delta"]:.3f}"
                if vehicle["delta"] < 0:
                    delta_display = f"  {vehicle["delta"]:.0f}"
            else:
                delta_display = f"{vehicle["delta"]:.3f}"

            color = "\033[90m" if vehicle["status"] != 1 else ""

            print(
                f"{color}"
                f"P{vehicle["running_position"]:<4}"
                f"#{vehicle["vehicle_number"]:<4}"
                f"{vehicle["driver"]["last_name"].replace("(i)", "").replace("#", "").replace("*", "").strip():<15}"
                f"{delta_display:<8}"
                f"{vehicle["last_lap_time"]:<8.3f}"
                f"{max((p["pit_in_leader_lap"] for p in vehicle["pit_stops"]), default=""):<5}"
                f"{vehicle["best_lap_time"]:<6.3f}|{vehicle["best_lap"]:<5}"
                f"{vehicle["sponsor_name"]:<8}"
                f"\033[0m"
            )

        next_check += 1
        if config.sleeper(max(0, next_check - monotonic())):
            stop_event.set()
            return

if __name__ == "__main__":
    main(False)
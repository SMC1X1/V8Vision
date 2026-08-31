from time import monotonic
from shutil import copyfile
from os.path import exists

from src import config


def main(race_id, lap_option, stop_event, ready_event):
    count = lap_option
    next_check = monotonic()

    while not stop_event.is_set():
        for name in config.FEEDS:
            source = (f"replay/{race_id}/{name}/{name}{count}.json")
            destination = (f"replay/{race_id}/{name}/{name}.json")
    
            if exists(source):
                copyfile(source, destination)

        if not ready_event.set():
            ready_event.set()

        count += 1
        next_check += config.INTERVAL

        wait_time = max(0, next_check - monotonic())

        stop_event.wait(wait_time)
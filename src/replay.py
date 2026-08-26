from time import monotonic
from shutil import copyfile
from os.path import exists
from src import config

def main(stop_event, race_id, lap_option):

    count = lap_option
    next_check = monotonic()

    while not stop_event.is_set():
        for name in config.feeds:
            source = f"replay/{race_id}/{name}/{name}{count}.json"
            destination = f"replay/{race_id}/{name}/{name}.json"

            if exists(source):
                copyfile(source, destination)
                if __name__ == "__main__":
                    print(f"Replayed {name}{count}")

        count += 1

        next_check += config.interval

        if __name__ == "__main__":
            if config.sleeper(max(0, next_check - monotonic())):
                return
        else:
            stop_event.wait(max(0, next_check - monotonic()))

if __name__ == "__main__":
    main()
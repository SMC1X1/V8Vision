from subprocess import run
from os import listdir, makedirs
from os.path import exists
import json

from src import leaderboard, record, recon


def main():
    while True:
        run("title V8Vision & cls", shell=True)

        print(
            f"\n"
            f"\033[1;33m     \033[1;31m  _  _ \033[1;34m  ___ \033[1;37m _   _____ _   ___     _          \n"
            f"\033[1;33m  / /\033[1;31m / // /\033[1;34m /   /\033[1;37m| | / ( _ ) | / (_)__ (_)__  ___  \n"
            f"\033[1;33m / / \033[1;31m/ // / \033[1;34m/   / \033[1;37m| |/ / _  | |/ / (_-</ / _ \\/ _ \\ \n"
            f"\033[1;33m/ / \033[1;31m/_//_/ \033[1;34m/___/  \033[1;37m|___/\\___/|___/_/___/_/\\___/_//_/ \n"
            f"\n"
            f"            - Live NASCAR Dashboard -\n"
            f"\n"
            f"\n"
            f"                  1. Live Feed\n"
            f"                  2. Replay\n"
            f"                  3. Record\n"
            f"                  4. Recon\n"
            f"\n"
        )

        option = input("               Choose an option: ")

        if option == "1":
            launch_feed()

        elif option == "2":
            launch_replay()

        elif option == "3":
            launch_record()

        elif option == "4":
            launch_recon()

        else:
            continue


def launch_feed():
    run("title V8Vision Live", shell=True)
    leaderboard.main(True, None, None)


def launch_replay():
    run("title V8Vision Replay & cls", shell=True)
    makedirs("replay", exist_ok=True)

    recordings = {}

    for number, folder in enumerate(sorted(listdir("replay")), 1):
        if folder.isdigit():
            race_id = int(folder)

            with open(
                f"replay/{race_id}/weekend-feed/weekend-feed1.json"
            ) as file:
                data = json.load(file)

            recordings[number] = {
                "race_id": data["weekend_race"][0]["race_id"],
                "year": data["weekend_race"][0]["race_season"],
                "race_name": data["weekend_race"][0]["race_name"],
                "track_name": data["weekend_race"][0]["track_name"]
            }

    for number, recording in recordings.items():
        print(
            f"\n{number}. "
            f"{recording['year']} "
            f"{recording['race_name']} - "
            f"{recording['track_name']}"
        )

    while True:
        try:
            replay_option = int(input("\nChoose a race: "))
            race_id = recordings[replay_option]["race_id"]
        except (ValueError, KeyError):
            break

        max_count = 0

        for filename in listdir(f"replay/{race_id}/live-feed"):
            number = filename.removeprefix("live-feed").removesuffix(".json")

            if number.isdigit():
                count = int(number)

                if count > max_count:
                    max_count = count

        try:
            lap_option = int(input("\nStarting Lap: "))

            for count in range(1, max_count + 1):
                if exists(f"replay/{race_id}/live-feed/live-feed{count}.json"):
                    with open(
                        f"replay/{race_id}/live-feed/live-feed{count}.json"
                    ) as file:
                        data = json.load(file)

                    if lap_option <= data["lap_number"]:
                        lap_option = count
                        break

        except ValueError:
            break

        leaderboard.main(False, race_id, lap_option)
        break


def launch_record():
    run("title V8Vision Record & cls", shell=True)

    print("\nThis will overwrite any recordings of the current race.")

    overwrite = input("\nEnter Y to continue: ")

    if overwrite.upper() == "Y":
        record.main()


def launch_recon():
    run("title V8Vision Recon & cls", shell=True)
    recon.main()


main()
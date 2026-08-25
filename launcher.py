from subprocess import run
from os import listdir, makedirs
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

            option = int(input("               Choose an option: "))

            if option == 1:
                run("title V8Vision Live", shell=True)
                leaderboard.main(True, None)

            elif option == 2:
                run("title V8Vision Replay & cls", shell=True)
                makedirs("replay", exist_ok=True)
                recordings = {}
                for number, folder in enumerate(sorted(listdir("replay")), 1):
                    if folder.isdigit():
                        race_id = int(folder)
                    with open(f"replay/{race_id}/weekend-feed/weekend-feed1.json") as file:
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
                    except:
                        break
                    leaderboard.main(False, race_id)
                    break

            elif option == 3:
                run("title V8Vision Record & cls", shell=True)
                print("\nThis will overwrite any current recordings of the current race. ")
                overwrite = input("\nEnter Y to continue: ")
                if overwrite.upper() == "Y":
                    run("title V8Vision Record & cls", shell=True)
                    record.main()
                else:
                    main()

            elif option == 4:
                run("title V8Vision Recon & cls", shell=True)
                recon.main()
                
            else:
                main()
main()
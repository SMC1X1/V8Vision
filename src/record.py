import requests
from time import monotonic
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from os import makedirs

from src import config


def main():
    makedirs("logs", exist_ok=True)
    with open("logs/record_log.txt", "w"):
        pass

    for name in config.FEEDS:
        makedirs(
            f"replay/{config.race_id}/{name}",
            exist_ok=True
        )

    next_check = monotonic()
    count = 1
    etags = {}

    with ThreadPoolExecutor(max_workers=len(config.FEEDS)) as executor:
        while True:

            results = executor.map(
                lambda feed: download_feed(feed, etags, count),
                config.FEEDS.items()
            )

            for result in results:
                if result:

                    print(result)

                    with open("logs/record_log.txt", "a") as log:
                        log.write(f"{result}\n")

            count += 1
            next_check += config.INTERVAL

            if config.sleeper(next_check - monotonic()):
                return


def download_feed(feed, etags, count):
    name, url = feed
    etag = etags.get(name)

    try:
        response = requests.get(
            url,
            headers={"If-None-Match": etag},
            timeout=10
        )

        if response.status_code == 304:
            return None

        response.raise_for_status()

        data = response.content
        etags[name] = response.headers.get("ETag")

        with open(
            f"replay/{config.race_id}/{name}/{name}{count}.json",
            "wb"
        ) as file:
            file.write(data)

        return f"{datetime.now()} Saved {name} snapshot {count}"

    except requests.RequestException as e:
        return f"{name} failed: {e}"
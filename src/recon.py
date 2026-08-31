import requests
from time import monotonic
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from os import makedirs

from src import config


def main():
    makedirs("logs", exist_ok=True)
    with open("logs/recon_log.txt", "w"):
        pass

    start_message = f"{datetime.now()} Recon Engaged..."
    print(start_message)

    with open("logs/recon_log.txt", "a") as log:
        log.write(start_message + "\n")

    next_check = monotonic()
    last_change = {name: next_check for name in config.FEEDS}
    etags = {}

    with ThreadPoolExecutor(max_workers=len(config.FEEDS)) as executor:
        while True:

            results = executor.map(
                lambda feed: check_feed(feed, etags, last_change),
                config.FEEDS.items()
            )

            for result in results:
                if result:

                    print(result)

                    with open("logs/recon_log.txt", "a") as log:
                        log.write(result + "\n")

            next_check += config.INTERVAL

            if config.sleeper(next_check - monotonic()):
                return


def check_feed(feed, etags, last_change):
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

        etags[name] = response.headers.get("ETag")

        now = monotonic()
        elapsed = now - last_change[name]
        last_change[name] = now

        return (f"{datetime.now()} {name} changed after {elapsed:.3f}s")

    except requests.RequestException as e:
        return f"{name} failed: {e}"
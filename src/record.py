import requests
from time import monotonic
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from os import makedirs
from src import config

def main():
    etags = {}

    for name in config.feeds:
        makedirs(f"replay/{config.race_id}/{name}", exist_ok=True)

    with open("record_log.txt", "w") as log:
        pass

    def download_feed(feed):
        name, url = feed

        etag = etags.get(name)

        try:
            headers = {"If-None-Match": etag} if etag else {}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 304:
                return None
            response.raise_for_status()

            data = response.content
            etags[name] = response.headers.get("ETag")

            with open(f"replay/{config.race_id}/{name}/{name}{count}.json", "wb") as file:
                file.write(data)

            return f"Saved {name} snapshot {count}"
        
        except requests.RequestException as e:
            return f"{name} failed: {e}"


    count = 1
    next_check = monotonic()

    with ThreadPoolExecutor(max_workers=len(config.feeds)) as executor:
        while True:
            timestamp = datetime.now()
            
            results = executor.map(download_feed, config.feeds.items())
            
            for result in results:
                if result:
                    print(f"{timestamp} {result}")
                    with open("record_log.txt", "a") as log:
                        log.write(f"{timestamp} {result}\n")

            count += 1
            next_check += config.interval
            if config.sleeper(max(0, next_check - monotonic())):
                return

if __name__ == "__main__":
    main()
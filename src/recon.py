import requests
from time import monotonic
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from src import config

def main():
    with open("recon_log.txt", "w") as log:
        pass
    next_check = monotonic()
    last_change = {name: next_check for name in config.feeds}
    etags = {}

    start_message = f"{datetime.now()} Recon Engaged..."
    print(start_message)
    with open("recon_log.txt", "a") as log:
        log.write(start_message + "\n")

    def check_feed(feed):
        name, url = feed
        etag = etags.get(name)

        try:
            response = requests.get(url, headers={"If-None-Match": etag}, timeout=10)

            if response.status_code == 304:
                return None
            response.raise_for_status()

            etags[name] = response.headers.get("ETag")
            now = monotonic()
            elapsed = now - last_change[name]
            last_change[name] = now

            return f"{datetime.now()} {name} changed after {elapsed:.3f}s"
        
        except requests.RequestException as e:
            return f"{name} failed: {e}"
        
    with ThreadPoolExecutor(max_workers=len(config.feeds)) as executor:
        while True:
            results = executor.map(check_feed, config.feeds.items())
            for result in results:
                if result:
                    print(result)
                    with open("recon_log.txt", "a") as log:
                        log.write(result + "\n")
            next_check += config.interval
            if config.sleeper(max(0, next_check - monotonic())):
                return
            
if __name__ == "__main__":
    main()
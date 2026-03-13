import requests
import re
import json
import os

URL = "https://sunabaco.com/event/"
DATA_FILE = "events.json"


def normalize_url(url):
    return url.split("?")[0].rstrip("/")


def extract_match(content, regex):
    m = re.search(regex, content)
    return m.group(1).strip() if m else ""


def get_old_urls():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE) as f:
        return json.load(f)


def save_urls(urls):
    with open(DATA_FILE, "w") as f:
        json.dump(urls, f)


def check_events():

    res = requests.get(URL)
    html = res.text

    cards = re.findall(
        r'<a href="https://sunabaco\.com/event/[^"]+"[\s\S]*?</a>',
        html
    )

    old_urls = [normalize_url(u) for u in get_old_urls()]

    new_events = []
    current_urls = []
    processed = set()

    for card in cards:

        link = re.search(r'href="([^"]+)"\s*title="([^"]+)"', card)
        if not link:
            continue

        event_url = normalize_url(link.group(1))

        if event_url in processed:
            continue

        processed.add(event_url)

        title = link.group(2)

        image = extract_match(card, r'src="([^"]+)"')
        details = extract_match(
            card,
            r'class="eventCard__info">([\s\S]*?)</div>'
        )

        details = re.sub("<[^>]+>", " ", details)

        current_urls.append(event_url)

        if event_url not in old_urls:
            new_events.append({
                "title": title,
                "url": event_url,
                "image": image,
                "details": details
            })

    save_urls(current_urls)

    return new_events


if __name__ == "__main__":
    events = check_events()

    if events:
        print("NEW EVENTS FOUND")
        for e in events:
            print(e["title"], e["url"])
    else:
        print("No new events")

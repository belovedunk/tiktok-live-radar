import asyncio
import json
import os
import urllib.parse
import urllib.request

from TikTokLive import TikTokLiveClient


USERS = {
    "chenjoong": {
        "name": "Joong",
        "url": "https://www.tiktok.com/@chenjoong",
    },
    "dunknatachai": {
        "name": "Dunk",
        "url": "https://www.tiktok.com/@dunknatachai",
    },
    "figothanatawan": {
        "name": "Figo",
        "url": "https://www.tiktok.com/@figothanatawan",
    },
}
}

STATE_FILE = "state.json"
BARK_KEY = os.environ["BARK_KEY"]


def load_state():
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {username: False for username in USERS}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def send_bark(name, url):
    title = f"🔴 {name} 開 LIVE 了！"
    body = f"點一下直接進入 {name} 的 TikTok LIVE"

    encoded_title = urllib.parse.quote(title)
    encoded_body = urllib.parse.quote(body)

    api_url = (
        f"https://api.day.app/{BARK_KEY}/"
        f"{encoded_title}/{encoded_body}"
        f"?url={urllib.parse.quote(url, safe='')}"
    )

    request = urllib.request.Request(api_url, method="GET")

    with urllib.request.urlopen(request, timeout=15) as response:
        print(f"Bark response: {response.status}")


async def check_user(username, info, state):
    client = TikTokLiveClient(unique_id=f"@{username}")

    try:
        live = await client.is_live()
        previous = state.get(username, False)

        print(f"{info['name']} (@{username}): LIVE={live}, previous={previous}")

        if live and not previous:
            send_bark(info["name"], info["url"])

        state[username] = live

    except Exception as e:
        print(f"Error checking @{username}: {e}")


async def main():
    state = load_state()

    for username, info in USERS.items():
        await check_user(username, info, state)

    save_state(state)


if __name__ == "__main__":
    asyncio.run(main())

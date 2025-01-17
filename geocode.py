""" Lookup coordinates for new locations using Nominatim (OpenStreetMap's geocoder). """

import httpx
import json
import re
from pathlib import Path
from ps_data import events, PSEvent
from time import sleep

NOMINATIM_ENDPOINT = "https://nominatim.openstreetmap.org/search"
CACHE_FILE = Path("./locations.json")


def update_locations() -> None:
    try:
        with CACHE_FILE.open("r") as f:
            cache = json.load(f)
    except FileNotFoundError:
        cache = {}

    changed = 0

    for event in events():
        if event.location is None:
            cache_key = event.address
        else:
            cache_key = event.location + ", " + event.address

        if cache_key in cache:
            continue

        location = geocode(event)
        if location is None:
            print("Unable to geocode location:", event.location, event.address)
            cache[cache_key] = {}
            continue

        coords = {"lon": location["lon"], "lat": location["lat"]}

        changed += 1

        print(f"Geocoded new location {event.location}, {event.address}:")
        print(
            f"Coords: {coords}, type: {location.get('type')} address: {location.get('display_name')}"
        )
        sleep(1)
        cache[cache_key] = coords

    with CACHE_FILE.open("w") as f:
        json.dump(cache, f, indent=4)

    print(f"Geocoded {changed} new locations.")


def geocode(event: PSEvent):
    if event.address is None:
        return None

    # Massage the address to satisfy Nominatim
    # Add a comma after the street number
    address = re.sub(r" ([0-9]+) ", r"\1,", event.address).split(",")
    # Try stripping off parts of the address to get it to match.
    queries = [
        f"{event.location}, {",".join(address)}",
        f"{event.location}, {",".join(address[1:])}",
        f"{event.location}, {",".join(address[2:])}",
        event.address,
    ]
    for query in queries:
        print(query)
        result = nominatim_geocode(query)
        if result is not None:
            return result
    return None


def nominatim_geocode(query: str):
    params = {
        "q": query,
        "countrycodes": "gb",
        "format": "jsonv2",
    }
    response = httpx.get(NOMINATIM_ENDPOINT, params=params)
    data = response.json()
    if len(data) == 0:
        return None
    return data[0]


if __name__ == "__main__":
    update_locations()

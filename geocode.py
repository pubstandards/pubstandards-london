"""Lookup coordinates for new locations using Nominatim (OpenStreetMap's geocoder)."""

import httpx
import json
import re
import sys
from pathlib import Path
from ps_data import events, PSEvent
from time import sleep

NOMINATIM_ENDPOINT = "https://nominatim.openstreetmap.org/search"
CACHE_FILE = Path("./locations.json")

# Simplified Pattern #2 from https://stackoverflow.com/a/51885364
POSTCODE_REGEX = r"[A-Z][A-HJ-Y]?\d[A-Z\d]? ?\d[A-Z]{2}|GIR ?0A{2}"


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
            print("\n!!! Unable to geocode location:", event.location, event.address)
            sys.exit(1)

        fields = {
            "lon": location["lon"],
            "lat": location["lat"],
            "osm_type": location["osm_type"],
            "osm_id": location["osm_id"],
        }

        osm_tag_data = osm_data(location["osm_type"], location["osm_id"])
        fields.update(osm_tag_data)

        changed += 1

        print(f"Geocoded new location {event.location}, {event.address}:")
        print(
            f"Coords: ({fields['lat']},{fields['lon']}) "
            + "type: {location.get('type')} "
            + "address: {location.get('display_name')}"
        )
        sleep(1)
        cache[cache_key] = fields

    with CACHE_FILE.open("w") as f:
        json.dump(cache, f, indent=4)

    print(f"Geocoded {changed} new locations.")


def geocode(event: PSEvent):
    if event.address is None:
        return None

    # Massage the address to satisfy Nominatim
    # Add a comma after the street number
    address = re.sub(r" ([0-9]+) ", r"\1,", event.address).split(",")

    # If a pub is called "Bricklayers Arms" Nominatim will refuse to find it
    # under "The Bricklayers Arms" so try both
    location_minus_the = re.sub(r"^The ", r"", event.location, flags=re.IGNORECASE)

    location_postcode = None
    matches = re.search(f" ({POSTCODE_REGEX})$", event.address, flags=re.IGNORECASE)
    if matches:
        location_postcode = matches.group(1)

    # Try stripping off parts of the address to get it to match.
    queries = [
        f"{event.location}, {",".join(address)}",
        f"{event.location}, {",".join(address[1:])}",
        f"{event.location}, {",".join(address[2:])}",
        f"{location_minus_the}, {",".join(address)}",
        f"{location_minus_the}, {",".join(address[1:])}",
        f"{location_minus_the}, {",".join(address[2:])}",
        event.address,
    ]
    for query in queries:
        print(query)
        result = nominatim_geocode(query)
        if result is not None:

            # Validate the postcode of the result matches our search, otherwise
            # people may end up in the wrong pub
            matches = re.search(
                f" ({POSTCODE_REGEX}),", result.get("display_name"), flags=re.IGNORECASE
            )
            if location_postcode and matches:
                # We ignore the last two characters as OSM often has postcodes slightly wrong
                if matches.group(1)[:-2] != location_postcode[:-2]:
                    print(
                        f" * Postcode {matches.group(1)} does not match, discarding result"
                    )
                    continue

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


def osm_data(osm_type: str, osm_id: int):
    response = httpx.get(
        f"https://www.openstreetmap.org/api/0.6/{osm_type}/{osm_id}.json"
    )
    data = response.json()
    if len(data) == 0:
        return None

    return {
        "wikidata_id": data["elements"][0]["tags"].get("wikidata"),
        "fhrs_id": data["elements"][0]["tags"].get("fhrs:id"),
        "website": data["elements"][0]["tags"].get("website"),
    }


if __name__ == "__main__":
    update_locations()

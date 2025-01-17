#!/usr/bin/env -S uv run -q
# /// script
# dependencies = [
#   "httpx",
#   "arrow",
# ]
# ///
#
# Called by IRCCat to handle the ?ps command in IRC.

import httpx
import arrow

data = httpx.get("https://london.pubstandards.com/next.json").json()

event = None

for e in data:
    datetime = arrow.get(e["date"] + " " + e["time"])
    event = e
    if datetime.date() >= arrow.now().date():
        break

if event is None:
    print("No upcoming events.")
    exit()

if datetime < arrow.now():
    msg = f"{event['title']} is happening right now at {event['location']}. Get to the pub!"
else:
    friendly_date = datetime.humanize(granularity=["day", "hour"])
    msg = f"{event['title']} is happening at {event['location']} {friendly_date}: "
    msg += f"https://london.pubstandards.com/event/{event['slug']}"

print(msg.encode("utf-8"))

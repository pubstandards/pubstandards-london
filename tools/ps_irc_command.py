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

now = arrow.now()

for e in data:
    datetime = arrow.get(e["date"] + " " + e["time"])
    event = e
    if datetime.date() >= now.date():
        break

if event is None:
    print("No upcoming events.")
    exit()

rsvp = event['rsvp_responses']

if datetime < now:
    msg = f"{event['title']} is happening right now at {event['location']}. Get to the pub!"
else:
    friendly_date = datetime.humanize(now)
    msg = f"{event['title']} is happening at {event['location']} {friendly_date}. "
    if rsvp['attending'] > 0:
        msg += f"{rsvp['attending']} people are coming"
    if rsvp['interested'] > 0:
        if rsvp['attending'] > 0:
            msg += ' and '
        msg += f"{rsvp['interested']} people are interested"
    if rsvp['attending'] > 0 or rsvp['interested'] > 0:
        msg += ": "
    msg += f"https://london.pubstandards.com/event/{event['slug']}"

print(msg)

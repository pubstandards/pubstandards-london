from collections.abc import Iterator
import datetime
from zoneinfo import ZoneInfo
import json
import heapq
from collections import (
    namedtuple,
    OrderedDict,
)
from typing import Optional
import markupsafe

import the_algorithm
from the_algorithm import HIATUSES
import roman
import slug
from dateutil.relativedelta import relativedelta

from util import combine_tz, utc_now, format_relative_time

Venue = namedtuple(
    "Venue", ["from_date", "until_date", "name", "address", "description"]
)

VENUES = [
    Venue(
        the_algorithm.FIRST_PUBSTANDARDS,
        HIATUSES[0][0],
        "The Bricklayers Arms",
        "31 Gresse Street, London W1T 1QS",
        "We'll meet in the upstairs room as usual.",
    ),
    Venue(
        HIATUSES[0][1],
        None,
        "The Miller",
        "96 Snowsfields, London SE1 3SS",
        "Outside if it's nice, inside if it's not.",
    ),
]

PS_STARTS = datetime.time(18, 0, 0)
PS_ENDS = datetime.time(23, 30, 0)
PS_TIMEZONE = "Europe/London"


class PSEvent(object):
    def __init__(
        self, data={}, date: Optional[datetime.date] = None, manual: bool = False
    ) -> None:
        if date is None:
            raise ValueError("date is required for a PSEvent")
        self.starts = PS_STARTS
        self.ends = PS_ENDS
        self.location = None
        self.address = None
        self.name = None
        self.description = None
        self.cancelled = False
        self.date: datetime.date = date
        self.manual = manual  # used for merging iters

        for k in ("name", "description", "location", "address"):
            if k in data:
                setattr(self, k, data[k])

        for k in ("starts", "ends"):
            if k in data and isinstance(data[k], str):
                setattr(self, k, datetime.datetime.strptime(data[k], "%H:%M").time())

        if "cancelled" in data:
            self.cancelled = bool(data["cancelled"])

        if self.location is None:
            for venue in VENUES:
                if venue.from_date < self.date and (
                    venue.until_date is None or venue.until_date > self.date
                ):
                    self.location = venue.name
                    self.address = venue.address
                    if self.description is None:
                        self.description = venue.description
                    break
            else:
                raise ValueError("No venue found for date {}".format(self.date))

        self.tzinfo = ZoneInfo(PS_TIMEZONE)

        # We use local timezones because the comparisons are minimal, we don't
        # use any timedeltas, and they're stored and displayed as local times.
        self.start_dt = combine_tz(self.date, self.starts, self.tzinfo)
        self.end_dt = combine_tz(self.date, self.ends, self.tzinfo)

    def __lt__(self, other):
        return self.date < other.date or (
            self.date == other.date and other.manual and not self.manual
        )

    @property
    def title(self) -> str:
        if self.name is None:
            offset = the_algorithm.ps_offset_from_date(self.date)
            return "Pub Standards " + roman.toRoman(offset)
        return self.name

    @property
    def slug(self):
        return slug.slug(self.title)

    @property
    def pretty_date(self):
        return "{dt:%A} {dt:%B} {dt.day}, {dt.year}".format(dt=self.start_dt)

    @property
    def pretty_time_period(self):
        return markupsafe.Markup(
            self.start_dt.strftime("%-I:%M %p")
            + "&ndash;"
            + self.end_dt.strftime("%-I:%M %p %Z")
        )

    @property
    def in_the_past(self):
        return utc_now() > self.end_dt

    @property
    def time_until(self):
        now = utc_now()
        relative = relativedelta(self.start_dt, now)

        if self.start_dt < now and now < self.end_dt:
            return "Happening right now! Get to the pub!"

        return format_relative_time(relative)


def load_ps_data():
    return json.load(open("ps_data.json"), object_pairs_hook=OrderedDict)


def get_ps_event_by_number(number):
    date = the_algorithm.ps_date_from_offset(number)
    stringdate = date.strftime("%Y-%m-%d")
    event_data = load_ps_data().get(stringdate, {})
    return PSEvent(event_data, date=datetime.date(date.year, date.month, date.day))


def get_ps_event_by_slug(slug):
    for stringdate, event in load_ps_data().items():
        date_obj = datetime.datetime.strptime(stringdate, "%Y-%m-%d").date()
        event = PSEvent(event, date=date_obj)
        if event.slug == slug:
            return event


def gen_events(start=None, end=None) -> Iterator[PSEvent]:
    if end is None:
        end = utc_now() + datetime.timedelta(days=3650)
    gen = the_algorithm.gen_ps_dates(start)
    event = PSEvent(date=next(gen))
    while not end or event.end_dt < end:
        yield event
        event = PSEvent(date=next(gen))


def get_manual_ps_events(start=None, end=None) -> Iterator[PSEvent]:
    for stringdate, event in load_ps_data().items():
        date_obj = datetime.datetime.strptime(stringdate, "%Y-%m-%d").date()
        event = PSEvent(event, date=date_obj, manual=True)
        if start and event.end_dt < start:
            continue
        if not end or event.end_dt < end:
            yield event


def merge_event_iters(
    one: Iterator[PSEvent], two: Iterator[PSEvent]
) -> Iterator[PSEvent]:
    events = heapq.merge(one, two)
    previous = None
    # In order to only return the manual event if it's intended to override an
    # algorithmic event, we only yield after we've inspected the next event
    for event in events:
        if previous:
            if previous.date == event.date:
                # we're overriding the previous event
                previous = event
                continue
            yield previous
        previous = event

    if previous:
        yield previous


def events(start=None, end=None) -> Iterator[PSEvent]:
    yield from merge_event_iters(
        get_manual_ps_events(start=start, end=end), gen_events(start=start, end=end)
    )
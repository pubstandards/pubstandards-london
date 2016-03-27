import datetime
import json
import heapq
from collections import OrderedDict
import pytz

import the_algorithm
import roman
import slug
from dateutil.relativedelta import relativedelta

from util import combine_tz, utc_now, format_relative_time

PS_LOCATION = 'The Bricklayers Arms'
PS_ADDRESS  = '31 Gresse Street, London W1T 1QS'
PS_STARTS   = datetime.time(18, 0, 0)
PS_ENDS     = datetime.time(23, 30, 0)
PS_TIMEZONE = 'Europe/London'

class PSEvent(object):
    """
    Represents a meeting on a particular date.
    For a scheduled event, construct with a date from the algorithm.
    Otherwise override the calendar by passing any date and event_data.

    >>> ps_100 = PSEvent(datetime.date(2014, 3, 13))
    >>> ps_100
    <PSEvent 2014-03-13>

    >>> ps_100 == PSEvent('2014-03-13')
    True

    >>> ps_100_named = PSEvent('2014-03-13', {'name': "PS 100"})
    >>> ps_100_named == ps_100
    False
    >>> ps_100_named
    <PSEvent 2014-03-13: 'PS 100'>
    """
    def __init__(self, date, event_data=None):
        if isinstance(date, basestring):
            self.date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        else:
            self.date = date

        self.starts      = PS_STARTS
        self.ends        = PS_ENDS
        self.location    = PS_LOCATION
        self.address     = PS_ADDRESS
        self.name        = None
        self.cancelled   = False

        if event_data is None:
            self.override = False

        else:
            self.override = True
            for k, v in event_data.items():
                if k in ('starts', 'ends') and isinstance(v, basestring):
                    v = datetime.datetime.strptime(v, '%H:%M').time()
                setattr(self, k, v)

        self.tzinfo = pytz.timezone(PS_TIMEZONE)

        # We use local timezones because the comparisons are minimal, we don't
        # use any timedeltas, and they're stored and displayed as local times.
        self.start_dt = combine_tz(self.date, self.starts, self.tzinfo)
        self.end_dt = combine_tz(self.date, self.ends, self.tzinfo)

    def __eq__(self, other):
        if self.override or other.override:
            return set(self.__dict__.items()) == set(other.__dict__.items())
        return self.date == other.date

    def __lt__(self, other):
        return self.date < other.date

    def __repr__(self):
        datestr = self.date.strftime('%Y-%m-%d')
        if self.override:
            return '<PSEvent %s: %r>' % (datestr, self.name)
        return '<PSEvent %s>' % datestr

    @property
    def title(self):
        if self.name is None:
            offset = the_algorithm.ps_offset_from_date(self.date)
            return 'Pub Standards ' + roman.toRoman(offset)
        return self.name

    @property
    def slug(self):
        return slug.slug(unicode(self.title))

    @property
    def pretty_date(self):
        return self.start_dt.strftime('%A %B %d, %Y')

    @property
    def pretty_time_period(self):
        return self.start_dt.strftime('%-I:%M%p') + ' - ' + self.end_dt.strftime('%-I:%M%p %Z')

    @property
    def in_the_past(self):
        return utc_now() > self.end_dt

    @property
    def time_until(self):
        now = utc_now()
        relative = relativedelta(self.start_dt, now)

        if self.start_dt < now and now < self.end_dt:
            return u'Happening right now! Get to the pub!'

        return format_relative_time(relative)

def load_ps_data():
    return json.load(
        open('ps_data.json'),
        object_pairs_hook=OrderedDict
    )

def get_ps_event_by_number(number):
    date = the_algorithm.ps_date_from_offset(number)
    stringdate = date.strftime('%Y-%m-%d')
    event_data = load_ps_data().get(stringdate, {})
    if event_data:
        return PSEvent(date, event_data)

    return PSEvent(date)

def get_ps_event_by_slug(slug):
    for stringdate, event in load_ps_data().items():
        event = PSEvent(stringdate, event)
        if event.slug == slug:
            return event

def gen_events(start=None, end=None):
    gen = the_algorithm.gen_ps_dates(start)
    # gen_ps_dates actually returns datetimes
    event = PSEvent(gen.next().date())
    while not end or event.end_dt < end:
        yield event
        event = PSEvent(gen.next().date())

def get_manual_ps_events(start=None, end=None):
    for stringdate, event in load_ps_data().items():
        event = PSEvent(stringdate, event)
        if start and event.end_dt < start:
            continue
        if end and event.end_dt >= end:
            continue
        yield event

# heapq.merge is not stable, however the merge guaranteed overrides will be sequential
def merge_event_iters(one, two):
    events = heapq.merge(one, two)
    previous = None
    for event in events:
        if previous:
            if previous.date == event.date:
                if event.override:
                    previous = event
                    continue
                else:
                    event = None
            yield previous
        previous = event
    yield previous

def events(start=None, end=None):
    return merge_event_iters(
        get_manual_ps_events(start=start, end=end),
        gen_events(start=start, end=end)
    )

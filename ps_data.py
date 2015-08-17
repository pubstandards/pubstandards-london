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
PS_DESCRIPTION = 'We\'ll meet in the upstairs room as usual.'

class PSEvent(object):
    def __init__(self, data={}, date=None, override=False):
        self.starts      = PS_STARTS
        self.ends        = PS_ENDS
        self.location    = PS_LOCATION
        self.address     = PS_ADDRESS
        self.name        = None
        self.description = PS_DESCRIPTION
        self.cancelled   = False
        self.override    = override  # used for merging iters

        if date is not None:
            data['date'] = date

        for k, v in data.items():
            if k == 'date' and isinstance(v, basestring):
                v = datetime.datetime.strptime(v, '%Y-%m-%d')
            if k in ('starts', 'ends') and isinstance(v, basestring):
                v = datetime.datetime.strptime(v, '%H:%M').time()
            setattr(self, k, v)

        self.tzinfo = pytz.timezone(PS_TIMEZONE)

        # We use local timezones because the comparisons are minimal, we don't
        # use any timedeltas, and they're stored and displayed as local times.
        self.start_dt = combine_tz(self.date, self.starts, self.tzinfo)
        self.end_dt = combine_tz(self.date, self.ends, self.tzinfo)

    def __lt__(self, other):
        return self.date.date() < other.date.date()

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
    return PSEvent(event_data, date=date)

def get_ps_event_by_slug(slug):
    for stringdate, event in load_ps_data().items():
        event = PSEvent(event, date=stringdate)
        if event.slug == slug:
            return event

def gen_events(start=None, end=None):
    gen = the_algorithm.gen_ps_dates(start)
    event = PSEvent(date=gen.next())
    while not end or event.end_dt < end:
        yield event
        event = PSEvent(date=gen.next())

def get_manual_ps_events(start=None, end=None):
    for stringdate, event in load_ps_data().items():
        event = PSEvent(event, date=stringdate, override=True)
        if start and event.end_dt < start:
            continue
        if not end or event.end_dt < end:
            yield event

# heapq.merge is not stable, however the merge guaranteed overrides will be sequential
def merge_event_iters(one, two):
    events = heapq.merge(one, two)
    previous = None
    for event in events:
        if previous:
            if previous.date.date() == event.date.date():
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

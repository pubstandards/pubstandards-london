import the_algorithm
from datetime import datetime
import pytz

def parse_datestr(datestr):
    return datetime.strptime(datestr, '%Y-%m-%d')

def is_algorithmic_ps_date(ev_datestr):
    # Fields required vary depending on whether this is Pub or Substandards
    # This should probably be separated out in the data for ease of testing
    ev_date = parse_datestr(ev_datestr)
    day = the_algorithm.calc_middle_thursday(ev_date.year, ev_date.month)
    return day == ev_date.day


def utc_datetime(year, month, day, hour=0, minute=0, second=0, microsecond=0):
    return datetime(year, month, day, hour, minute, second, microsecond, pytz.UTC)


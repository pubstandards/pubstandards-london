from datetime import datetime
import pytz


def combine_tz(date, time, tzinfo):
    dt = datetime.combine(date, time)
    return tzinfo.localize(dt, is_dst=None)

def utc_now():
    return datetime.utcnow().replace(tzinfo=pytz.UTC)

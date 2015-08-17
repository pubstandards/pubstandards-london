from datetime import datetime
import pytz
import inflect

p = inflect.engine()

def combine_tz(date, time, tzinfo):
    dt = datetime.combine(date, time)
    return tzinfo.localize(dt, is_dst=None)

def utc_now():
    return datetime.utcnow().replace(tzinfo=pytz.UTC)

def format_relative_time(relative):
    date_part_names = 'year month day hour minute'.split()

    date_parts = zip(date_part_names, [getattr(relative, date_part+'s') for date_part in date_part_names])
    formatted = [p.no(date_part, value) for (date_part, value) in date_parts if value]

    rest, tail = formatted[:-1], formatted[-1]

    if rest:
        return u'In %s, and %s' % ( ', '.join(rest), tail )
    else:
        return u'In %s' % ( tail )

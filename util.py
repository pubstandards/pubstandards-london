from datetime import datetime, time, date, timezone
import inflect

p = inflect.engine()


def combine_tz(date: date, time: time, tzinfo) -> datetime:
    return datetime.combine(date, time, tzinfo)


def utc_now():
    return datetime.now(timezone.utc)


def format_relative_time(relative):
    date_part_names = "year month day hour".split()

    date_parts = zip(
        date_part_names,
        [getattr(relative, date_part + "s") for date_part in date_part_names],
    )
    formatted = [p.no(date_part, value) for (date_part, value) in date_parts if value]

    if len(formatted) < 2:
        return "Happening soon"

    rest, tail = formatted[:-1], formatted[-1]

    if rest:
        return "In %s, and %s" % (", ".join(rest), tail)
    else:
        return "In %s" % (tail)

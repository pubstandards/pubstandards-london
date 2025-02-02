#!/usr/bin/python
import datetime

import roman
import flask
from werkzeug.routing import BaseConverter
from flask_assets import Environment
from icalendar import Calendar, Event

import ps_data

from util import utc_now

app = flask.Flask(__name__)

assets = Environment()
assets.init_app(app)


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters["regex"] = RegexConverter


@app.route("/")
def homepage():
    try:
        next_event = next(next_events())
    except StopIteration:
        next_event = None
    return flask.render_template("homepage.html", event=next_event)


@app.route("/next")
def next_event():
    return flask.render_template("next.html", events=next_events())


@app.route("/previous")
def previous():
    coordinates = list(ps_data.LOCATIONS.values())
    events = ps_data.events(end=utc_now())
    return flask.render_template(
        "previous.html", events=events, events_coordinates=coordinates
    )


@app.route("/next.ics")
@app.route("/all.ics")
def ics():
    next_year = utc_now() + datetime.timedelta(weeks=52)
    return events_to_ical(ps_data.events(end=next_year), "Pub Standards Events")


@app.route("/next.json")
def next_json():
    return flask.jsonify([event.json() for event in next_events()])


@app.route('/event/pub-standards-<regex("[ivxcdmlIVXCDML]+"):numeral>')
def ps_event(numeral):
    try:
        number = roman.fromRoman(numeral.upper())
    except roman.InvalidRomanNumeralError:
        return "Invalid roman numeral!", 400

    event = ps_data.get_ps_event_by_number(number)
    return flask.render_template("event.html", event=event)


@app.route("/event/<slug>")
def other_event(slug):
    event = ps_data.get_ps_event_by_slug(slug)
    if not event:
        return "Unknown event", 404
    return flask.render_template("event.html", event=event)


@app.route("/keep-in-touch")
def keep_in_touch():
    return flask.render_template("keep-in-touch.html")


@app.route("/about")
def about():
    return flask.render_template("about.html", venues=ps_data.VENUES)


def next_events():
    now = utc_now()
    future = now + datetime.timedelta(weeks=52 * 10)
    return ps_data.events(start=now, end=future)


def events_to_ical(events, title):
    cal = Calendar()
    cal.add("summary", title)
    cal.add("X-WR-CALNAME", title)
    cal.add("X-WR-CALDESC", title)
    cal.add("version", "2.0")

    for event in events:
        url = f"https://london.pubstandards.com/event/{event.slug}"
        description = f"{event.description}\n\n{url}"
        issue_url = event.attendance_issue_url
        if issue_url:
            description += f"\n\nRSVP: {issue_url}"

        cal_event = Event()
        cal_event.add("uid", "%s-%s" % (event.slug, event.date))
        cal_event.add("summary", event.title)
        cal_event.add("description", f"{event.description}\n\n{url}")
        cal_event.add("url", url)
        cal_event.add("location", event.location + ", " + event.address)
        cal_event.add("dtstart", event.start_dt)
        cal_event.add("dtend", event.end_dt)
        cal.add_component(cal_event)

    return cal.to_ical(), 200, {"Content-Type": "text/calendar"}


if __name__ == "__main__":
    app.run(debug=True)

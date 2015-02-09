#!/usr/bin/python
import datetime

import roman
import flask
from icalendar import Calendar, Event

import ps_data

app = flask.Flask(__name__)

@app.route('/')
def homepage():
    return flask.render_template('homepage.html', event=next_events().next())

@app.route('/next')
def next():
    return flask.render_template('next.html', events=next_events())

@app.route('/previous')
def previous():
    events = ps_data.events(end=datetime.datetime.now())
    return flask.render_template('previous.html', events=events)

@app.route('/next.ics')
@app.route('/all.ics')
def ics():
    next_year = datetime.datetime.now() + datetime.timedelta(weeks=52)
    return events_to_ical(ps_data.events(end=next_year), 'Pub Standards Events')

@app.route('/event/pub-standards-<numeral>')
def ps_event(numeral):
    try:
        number = roman.fromRoman(numeral.upper())
    except roman.InvalidRomanNumeralError:
        return "Invalid roman numeral!", 400

    event = ps_data.get_ps_event_by_number(number)
    return flask.render_template('event.html', event=event)

@app.route('/event/<slug>')
def other_event(slug):
    event = ps_data.get_ps_event_by_slug(slug)
    if not event:
        return "Unknown event", 404
    return flask.render_template('event.html', event=event)

@app.route('/keep-in-touch')
def keep_in_touch():
    return flask.render_template('keep-in-touch.html')

@app.route('/about')
def about():
    return flask.render_template('about.html')


def next_events():
    now = datetime.datetime.now()
    future = now + datetime.timedelta(weeks=52)
    return ps_data.events(start=now, end=future)

def events_to_ical(events, title):
    cal = Calendar()
    cal.add('summary', title)
    cal.add('X-WR-CALNAME', title)
    cal.add('X-WR-CALDESC', title)
    cal.add('version', '2.0')
    for event in events:
        cal_event = Event()
        cal_event.add('uid', event.slug)
        cal_event.add('summary', event.title)
        cal_event.add('location', event.location + ", " + event.address)
        cal_event.add('dtstart', event.datetime['starts'])
        cal_event.add('dtend', event.datetime['ends'])
        cal.add_component(cal_event)

    return cal.to_ical(), 200, {'Content-Type': 'text/calendar'}

if __name__ == '__main__':
    app.run(debug=True)

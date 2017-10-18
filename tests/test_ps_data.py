import unittest
import ps_data
from test_util import parse_datestr, is_algorithmic_ps_date, utc_datetime
from datetime import datetime, timedelta
import pytz

class ValidateData(unittest.TestCase):
    required_fields = ['name', 'location', 'address']
    optional_fields = ['description', 'starts', 'ends', 'cancelled']

    def setUp(self):
        self.events = ps_data.load_ps_data()

    def test_required_fields(self):
        valid_fields = self.required_fields + self.optional_fields

        for datestr, event in self.events.items():
            if is_algorithmic_ps_date(datestr):
                print 'Checking override event %s: %s' % (datestr, event)
            else:
                print 'Checking additional event %s: %s' % (datestr, event)

            checked_fields = set()
            for field in event:
                assert field in valid_fields, '%r is not valid (%s)' % (field, valid_fields)
                assert field not in checked_fields, 'Duplicate field %r' % field
                checked_fields.add(field)

            if is_algorithmic_ps_date(datestr):
                pass

            else:
                for field in self.required_fields:
                    assert field in checked_fields, 'Required field %r missing from %r' % (field, checked_fields)

    def test_name_unique(self):
        # Names have to be unique as they're part of the URL

        seen_names = set()
        for datestr, event in self.events.items():
            if is_algorithmic_ps_date(datestr):
                if 'name' in event:
                    name = event['name']
                    assert 'Pub Standards' in name, 'Unexpected name %s' % name

            else:
                name = event['name']
                assert name is not None, 'Manual event has no name'
                assert name not in seen_names, 'Name %r is not unique' % name
                assert not name.startswith('Pub Standards '), 'Attempt to override name %r' % name
                seen_names.add(name)

    def test_events_in_order(self):
        datestrs = list(self.events)
        dates = map(parse_datestr, datestrs)

        assert dates == sorted(dates), 'Events are not in date order'
        assert datestrs == sorted(datestrs), 'Events are not in strict order'

    def test_invalid_times(self):
        def combine_tz(date, time, tzinfo):
            dt = datetime.combine(date, time)
            return tzinfo.localize(dt, is_dst=None)

        for datestr, event in self.events.items():

            event_date = datetime.strptime(datestr, '%Y-%m-%d')
            tzinfo = pytz.timezone('Europe/London')
            if 'starts' in event:
                starts = datetime.strptime(event['starts'], '%H:%M').time()
                combine_tz(event_date, starts, tzinfo)

            if 'ends' in event:
                ends = datetime.strptime(event['ends'], '%H:%M').time()
                combine_tz(event_date, ends, tzinfo)


class TestLookups(unittest.TestCase):

    def test_events_construct(self):
        manual_events = list(ps_data.get_manual_ps_events())

        next_year = datetime.utcnow().replace(tzinfo=pytz.UTC) + timedelta(weeks=52)
        # Add a minute to the last manual_event because events uses <
        end = max(next_year, manual_events[-1].end_dt + timedelta(minutes=1))
        all_events = list(ps_data.events(end=end))

        # As there's no __eq__ for PSEvent yet
        manual_start_dts = [e.start_dt for e in manual_events]
        all_start_dts = [e.start_dt for e in all_events]

        assert set(all_start_dts) > set(manual_start_dts)

    def test_override(self):
        ps_100 = ps_data.get_ps_event_by_number(100)
        assert 'ONE HUNDREDTH' in ps_100.description

    # For now, don't test .date, as it's either date() or datetime(),
    # depending on whether the event is from the algorithm or not

    def assertStartsAt(self, event, dt):
        assert event.start_dt == dt, '%r is wrong start time' % event.start_dt

    def test_ps_ranges(self):
        first_ps = ps_data.gen_events(start=utc_datetime(2005, 12, 14)).next()
        self.assertStartsAt(first_ps, utc_datetime(2005, 12, 15, 18, 0))

        second_ps = ps_data.gen_events(start=utc_datetime(2005, 12, 16)).next()
        self.assertStartsAt(second_ps, utc_datetime(2006, 1, 12, 18, 0))

    def test_ps_ranges_same_day(self):
        first_ps = ps_data.gen_events(start=utc_datetime(2005, 12, 15)).next()
        self.assertStartsAt(first_ps, utc_datetime(2005, 12, 15, 18, 0))

    def test_manual_ps_ranges(self):
        first_manual_ps = ps_data.get_manual_ps_events(start=utc_datetime(2006, 9, 25)).next()
        self.assertStartsAt(first_manual_ps, utc_datetime(2006, 9, 25, 17, 0))

        second_manual_ps = ps_data.get_manual_ps_events(start=utc_datetime(2006, 9, 26)).next()
        self.assertStartsAt(second_manual_ps, utc_datetime(2007, 2, 1, 18, 0))

    def test_merged_ranges_algorithmic(self):
        first_ps = ps_data.events(start=utc_datetime(2005, 12, 14)).next()
        self.assertStartsAt(first_ps, utc_datetime(2005, 12, 15, 18, 0))

        second_ps = ps_data.events(start=utc_datetime(2005, 12, 16)).next()
        self.assertStartsAt(second_ps, utc_datetime(2006, 1, 12, 18, 0))

    def test_merged_ranges_algorithmic_same_day(self):
        first_ps = ps_data.events(start=utc_datetime(2005, 12, 15)).next()
        self.assertStartsAt(first_ps, utc_datetime(2005, 12, 15, 18, 0))

    def test_merged_ranges_manual(self):
        first_manual_ps = ps_data.events(start=utc_datetime(2006, 9, 24)).next()
        self.assertStartsAt(first_manual_ps, utc_datetime(2006, 9, 25, 17, 0))

        first_manual_ps = ps_data.events(start=utc_datetime(2006, 9, 25)).next()
        self.assertStartsAt(first_manual_ps, utc_datetime(2006, 9, 25, 17, 0))

        first_post_manual_ps = ps_data.events(start=utc_datetime(2006, 9, 26)).next()
        self.assertStartsAt(first_post_manual_ps, utc_datetime(2006, 10, 12, 17, 0))

    def test_substandards_slug(self):
        ss_pista = ps_data.get_ps_event_by_slug('substandards-pista')
        self.assertStartsAt(ss_pista, utc_datetime(2007, 2, 1, 18, 0))

        assert ps_data.get_ps_event_by_slug('substandards-Pista') is None, 'Invalid slug matched'

    def test_substandards_slug_with_hyphens(self):
        first_ss = ps_data.get_ps_event_by_slug('mid-pub-standards-non-pub-standards-pub-standards')
        self.assertStartsAt(first_ss, utc_datetime(2006, 9, 25, 17, 0))

    @unittest.skip('Currently no way to test PS slugs')
    def test_manual_ps_slugs(self):
        ps_65 = ps_data.get_ps_event_by_slug('pubstandards-lxv')
        self.assertStartsAt(ps_65, utc_datetime(2005, 12, 14, 18, 0))

        ps_100 = ps_data.get_ps_event_by_slug('pubstandards-c')
        self.assertStartsAt(ps_100, utc_datetime(2014, 3, 13, 18, 0))

    def test_cancelled_event(self):
        ss_pista = ps_data.get_ps_event_by_slug('substandards-pista')
        assert ss_pista.cancelled is False

        ss_parklife = ps_data.get_ps_event_by_slug('substandards-parklife')
        assert ss_parklife.cancelled is True

    def assertAllEqual(self, items):
        assert len(set(list(items))) == 1, 'Not all items are equal: %r' % items

    def test_around_dst(self):
        def get_ev_data(ev):
            return (ev.start_dt,
                    ev.end_dt,
                    ev.slug,
                    ev.pretty_date,
                    ev.pretty_time_period,
                    )

        def check_events_for_starts(ev_getter, starts):
            ev_gens = map(ev_getter, starts)
            ev_lists = map(list, ev_gens)
            self.assertAllEqual(len(l) for l in ev_lists)

            for evs in zip(*ev_lists):
                ev_datas = map(get_ev_data, evs)
                self.assertAllEqual(ev_datas)

        def check_event_queries_for_starts(starts):
            # NB we don't test the_algorithm.next_ps_date, but
            # everything else about it should be deterministic
            def get_all_evs(start):
                future = start + timedelta(weeks=52)
                return ps_data.events(end=future)

            def get_next_evs(start):
                future = start + timedelta(weeks=52)
                return ps_data.events(start=start, end=future)

            def get_prev_evs(start):
                return ps_data.events(end=start)

            check_events_for_starts(get_all_evs, starts)
            check_events_for_starts(get_next_evs, starts)
            check_events_for_starts(get_prev_evs, starts)

        begin_dst = [
            utc_datetime(2014, 3, 30, 0, 30),
            utc_datetime(2014, 3, 30, 1, 30),
            utc_datetime(2014, 3, 30, 2, 30),
        ]
        end_dst = [
            utc_datetime(2014, 10, 26, 0, 30),
            utc_datetime(2014, 10, 26, 1, 30),
            utc_datetime(2014, 10, 26, 2, 30),
        ]

        check_event_queries_for_starts(begin_dst)
        check_event_queries_for_starts(end_dst)


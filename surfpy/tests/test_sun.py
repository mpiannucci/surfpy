from unittest import TestCase
import pytz
import datetime

import surfpy

class TestSunForecast(TestCase):
    def test_narragansett_forecast(self):
        ri_location = surfpy.Location(41.6, -71.5, altitude=10.0, name='Narragansett Pier')
        ri_tz = pytz.timezone('America/New_York')
        ri_sun = surfpy.Sun(ri_location)
        today_dt = datetime.datetime.today()
        today_d = datetime.date.today()
        today_sunrise = pytz.utc.localize(datetime.datetime.combine(today_d, ri_sun.sunrise(today_dt)))
        today_sunset = pytz.utc.localize(datetime.datetime.combine(today_d, ri_sun.sunset(today_dt)))

        #self.assertTrue(today_sunset > today_sunrise)
        
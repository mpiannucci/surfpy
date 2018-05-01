import os
import sys
sys.path.insert(0, os.path.abspath(__file__))

from .sun import Sun
from .location import Location
import pytz
import datetime


if __name__ == '__main__':
    ri_location = Location(41.6, -71.5, alt=10.0, name='Narragansett Pier')
    ri_tz = pytz.timezone('America/New_York')
    ri_sun = Sun(ri_location)
    today_dt = datetime.datetime.today()
    today_d = datetime.date.today()
    today_sunrise = pytz.utc.localize(datetime.datetime.combine(today_d, ri_sun.sunrise(today_dt)))
    today_sunset = pytz.utc.localize(datetime.datetime.combine(today_d, ri_sun.sunset(today_dt)))

    print('Todays Sunrise: ' + today_sunrise.astimezone(ri_tz).strftime('%H:%M %z'))
    print('Todays Sunset: ' + today_sunset.astimezone(ri_tz).strftime('%H:%M %z'))
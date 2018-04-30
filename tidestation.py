from .basestation import BaseStation
from . import units
from .tideevent import TideEvent
import datetime
import json
import pytz
try:
    import requests
except:
    pass


class TideStation(BaseStation):

    # https://tidesandcurrents.noaa.gov/api/datagetter?begin_date=20180429%2000:00&end_date=20180501%2000:00&station=8454000&product=predictions&datum=MTL&interval=hilo&units=english&time_zone=gmt&application=web_services&format=json
    _base_tide_url = 'https://tidesandcurrents.noaa.gov/api/datagetter?begin_date={0}%20{1}&end_date={2}%20{3}&station={4}&product=predictions&datum={5}&interval={6}&units={7}&time_zone=gmt&application=web_services&format=json'

    class DataInterval:
        default=''
        hourly='h'
        high_low='hilo'

    class TideDatum:
        mean_higher_high_water='MHHW'
        mean_high_water='MHW'
        mean_tide_level='MTL'
        mean_sea_level='MSL'
        mean_low_water='MLW'
        mean_lower_low_water='MLLW'

    def __init__(self, station_id, location, state=''):
        super(TideStation, self).__init__(station_id, location)

        self.state = state
        self.tidal_data = []
        self.tidal_events = []
    
    def create_tide_data_url(self, start_date, end_date, datum=TideDatum.mean_tide_level, interval=DataInterval.high_low, unit=units.Units.metric):
        start_date_str = start_date.strftime('%Y%m%d')
        start_time_str = start_date.strftime('%H:%M')
        end_date_str = end_date.strftime('%Y%m%d')
        end_time_str = end_date.strftime('%H:%M')
        url = self._base_tide_url.format(start_date_str, start_time_str, end_date_str, end_time_str, self.station_id. datum, interval, unit)
        return url

    def parse_tide_data(self, raw_data, datum, unit):
        if raw_data is None:
            return False
        elif raw_data == '':
            return False
        
        raw_json = json.loads(raw_data)
        if not 'predictions' in raw_json:
            return False
        
        tide_datas = raw_json['predictions']
        for data in tide_datas:
            event = TideEvent(unit)
            event.date = pytz.utc.localize(datetime.datetime.strptime(data['t'], '%Y-%m-%d %H:%M'))
            event.water_level = float(data['v'])
            event.water_level_datum = datum
            if 'type' in data:
                event.tidal_event = data['type']
                self.tidal_events.append(event)
            self.tidal_data.append(event)

        if len(self.tidal_events) < 1 and len(self.tidal_data) < 1:
            return False

        return True

    def fetch_tide_data(self, start_date, end_date, datum=TideDatum.mean_tide_level, interval=DataInterval.high_low, unit=units.Units.metric):
        url = self.create_tide_data_url(start_date, end_date, datum=datum, interval=interval, unit=units)
        response = requests.get(url)
        if len(response.text) < 1:
            return False
        return self.parse_tide_data(response.text, datum, unit)
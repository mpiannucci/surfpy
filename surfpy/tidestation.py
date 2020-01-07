from .basestation import BaseStation
from . import units
from . import tools
from .tideevent import TideEvent
import datetime
import json
import pytz
try:
    import requests
except:
    pass


class TideStation(BaseStation):

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
    
    def create_tide_data_url(self, start_date, end_date, datum=TideDatum.mean_tide_level, interval=DataInterval.high_low, unit=units.Units.metric):
        start_date_str = start_date.strftime('%Y%m%d')
        start_time_str = start_date.strftime('%H:%M')
        end_date_str = end_date.strftime('%Y%m%d')
        end_time_str = end_date.strftime('%H:%M')
        url = self._base_tide_url.format(start_date_str, start_time_str, end_date_str, end_time_str, self.station_id, datum, interval, unit)
        return url

    def parse_tide_data(self, raw_data, datum, unit):
        if raw_data is None:
            print('Failed to parse tidal data')
            return None
        elif raw_data == '':
            print('Failed to parse tidal data')
            return None
        
        raw_json = json.loads(raw_data)
        if not 'predictions' in raw_json:
            print('Failed to parse tidal data')
            return None
        
        tide_datas = raw_json['predictions']
        tidal_data = []
        tidal_events = []
        for data in tide_datas:
            event = TideEvent(unit)
            event.date = pytz.utc.localize(datetime.datetime.strptime(data['t'], '%Y-%m-%d %H:%M'))
            event.water_level = float(data['v'])
            event.water_level_datum = datum
            if 'type' in data:
                event.tidal_event = data['type']
                tidal_events.append(event)
            tidal_data.append(event)

        if len(tidal_data) < 1:
            print('Failed to parse tidal data')
            return None
        
        if len(tidal_events) < 1:
            tidal_events = self.interpolate_tidal_events(tidal_data)
            
        return tidal_events, tidal_data

    @staticmethod
    def interpolate_tidal_events(tidal_data):
        if len(tidal_data) < 1:
            print('Failed to interpolate tidal events')
            return None

        levels = [x.water_level for x in tidal_data]
        low_indexes, low_values, high_indexes, high_values = tools.peakdetect(levels, delta=0.05)

        tidal_events = []
        for i in low_indexes:
            low_tidal_event = tidal_data[i]
            low_tidal_event.tidal_event=TideEvent.TidalEventType.low_tide
            tidal_events.append(low_tidal_event)
        for i in high_indexes:
            high_tidal_event = tidal_data[i]
            high_tidal_event.tidal_event=TideEvent.TidalEventType.high_tide
            tidal_events.append(high_tidal_event)

        tidal_events.sort(key=lambda x: x.date)

        return tidal_events

    def fetch_tide_data(self, start_date, end_date, datum=TideDatum.mean_tide_level, interval=DataInterval.high_low, unit=units.Units.metric):
        url = self.create_tide_data_url(start_date, end_date, datum=datum, interval=interval, unit=unit)
        response = requests.get(url)
        if len(response.text) < 1:
            return False
        return self.parse_tide_data(response.text, datum, unit)

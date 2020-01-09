import datetime
import numpy as np
import matplotlib.pyplot as plt

import surfpy


class TidePlots(object):

    def __init__(self):
        _stations = surfpy.TideStations()
        _stations.fetch_stations()

        self.stations = {}
        self.data = {}
        for station in _stations.stations:
            self.stations[station.station_id] = station

    def fetch_water_level_data(self, station_id, start_date, end_date):
        self.data[station_id] = self.stations[station_id].fetch_tide_data(start_date, end_date, interval=surfpy.TideStation.DataInterval.default, unit=surfpy.units.Units.english)
        return len(self.data[station_id][0]) > 0

    def fetch_tidal_data(self, station_id, start_date, end_date):
        self.data[station_id] = self.stations[station_id].fetch_tide_data(start_date, end_date, interval=surfpy.TideStation.DataInterval.high_low, unit=surfpy.units.Units.english)
        return len(self.data[station_id][0]) > 0

    def plot_tidal_events(self, station_id):
        tidal_events, tidal_data = self.data[station_id]
        if tidal_events is None:
            return

        raw_dates = [x.date for x in tidal_events]
        raw_levels = [x.water_level for x in tidal_events]

        x = mdates.date2num(raw_dates)
        z4 = np.polyfit(x, raw_levels, len(raw_levels)-1)
        p4 = np.poly1d(z4)
        xx = np.linspace(x.min(), x.max(), 100)
        dd = mdates.num2date(xx)

        plt.figure(1)
        plt.title('Station ' + station_id + ': Water Level (ft)')
        plt.xlabel('Date')
        plt.ylabel('Water Level (ft)')
        plt.plot(dd, p4(xx))
        plt.scatter(raw_dates, raw_levels, c='r')
        
        plt.grid()
        plt.show()
        plt.gcf().clear()

    def plot_water_level(self, station_id):
        tidal_events, tidal_data = self.data[station_id]
        if tidal_data is None:
            return

        dates = [x.date for x in tidal_data]
        levels = [x.water_level for x in tidal_data]
        low_dates = [x.date for x in tidal_events if x.tidal_event == surfpy.TideEvent.TidalEventType.low_tide]
        low_levels = [x.water_level for x in tidal_events if x.tidal_event== surfpy.TideEvent.TidalEventType.low_tide]
        high_dates = [x.date for x in tidal_events if x.tidal_event == surfpy.TideEvent.TidalEventType.high_tide]
        high_levels = [x.water_level for x in tidal_events if x.tidal_event == surfpy.TideEvent.TidalEventType.high_tide]
        
        plt.figure(1)
        plt.title('Station ' + station_id + ': Water Level (ft)')
        plt.xlabel('Date')
        plt.ylabel('Water Level (ft)')
        plt.plot(dates, levels)
        plt.scatter(low_dates, low_levels, c='r')
        plt.scatter(high_dates, high_levels, c='g')
        
        plt.grid()
        plt.show()
        plt.gcf().clear()


if __name__ == '__main__':
    stations = TidePlots()
    newport_station_id = '8452660'
    today = datetime.datetime.today()
    ending_date = today + datetime.timedelta(days=8)

    #if stations.fetch_tidal_data(newport_station_id, today, ending_date):
    #    stations.plot_tidal_events(newport_station_id)
    #else:
    #    print('Failed to fetch tidal event data from ' + newport_station_id)
    
    if stations.fetch_water_level_data(newport_station_id, today, ending_date):
        stations.plot_water_level(newport_station_id)
    else:
        print('Failed to fetch water level data from ' + newport_station_id)

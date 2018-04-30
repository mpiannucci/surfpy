import os
import sys
sys.path.insert(0, os.path.abspath(__file__))

from .tidestations import TideStations
from .tidestation import TideStation
from . import units
from . import tools

import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


class TidePlots(object):

    def __init__(self):
        _stations = TideStations()
        _stations.fetch_stations()

        self.stations = {}
        for station in _stations.stations:
            self.stations[station.station_id] = station

    def fetch_water_level_data(self, station_id, start_date, end_date):
        return self.stations[station_id].fetch_tide_data(start_date, end_date, interval=TideStation.DataInterval.default, unit=units.Units.english)

    def fetch_tidal_data(self, station_id, start_date, end_date):
        return self.stations[station_id].fetch_tide_data(start_date, end_date, interval=TideStation.DataInterval.high_low, unit=units.Units.english)

    def plot_tidal_events(self, station_id):
        station = self.stations[station_id]
        if station is None:
            return

        raw_dates = [x.date for x in station.tidal_events]
        raw_levels = [x.water_level for x in station.tidal_events]

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
        station = self.stations[station_id]
        if station is None:
            return

        dates = [x.date for x in station.tidal_data]
        levels = [x.water_level for x in station.tidal_data]

        low_indexes, low_values, high_indexes, high_values = tools.peakdetect(levels, delta=0.05)
        low_dates = [dates[i] for i in low_indexes]
        high_dates = [dates[i] for i  in high_indexes]

        plt.figure(1)
        plt.title('Station ' + station_id + ': Water Level (ft)')
        plt.xlabel('Date')
        plt.ylabel('Water Level (ft)')
        plt.plot(dates, levels)
        plt.scatter(low_dates, low_values, c='r')
        plt.scatter(high_dates, high_values, c='g')
        
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

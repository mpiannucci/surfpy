import os
import sys
sys.path.insert(0, os.path.abspath(__file__))

from . import wavemodel
from . import weathermodel
from . import tools
from . import units
from .location import Location

import matplotlib.pyplot as plt


if __name__=='__main__':
    ri_wave_location = Location(41.4, -71.45, alt=30.0, name='Block Island Sound')
    ri_wave_location.depth = 30.0
    ri_wave_location.angle = 145.0
    ri_wave_location.slope = 0.02
    ec_wave_model = wavemodel.us_east_coast_wave_model()

    print('Fetching WW3 Wave Data')
    if ec_wave_model.fetch_grib_datas(ri_wave_location, 0, 60):
        data = ec_wave_model.to_buoy_data()
    else:
        print('Failed to fetch wave forecast data')
        sys.exit(1)

    print('Fetching GFS Weather Data')
    ri_wind_location = Location(41.6, -71.5, alt=10.0, name='Narragansett Pier')
    gfs_model = weathermodel.global_gfs_model()
    if gfs_model.fetch_grib_datas(ri_wind_location, 0, 60):
        gfs_model.fill_buoy_data(data)
    else:
        print('Failed to fetch wind forecast data')
        #sys.exit(1)

    # for dat in data:
    #     dat.solve_breaking_wave_heights(ri_wave_location)
    #     dat.change_units(units.Units.english)
    # json_data = tools.dump_json(data)
    # with open('forecast.json', 'w') as outfile:
    #     outfile.write(json_data)

    # maxs =[x.maximum_breaking_height for x in data]
    # mins = [x.minimum_breaking_height for x in data]
    # times = [x.date for x in data]

    # plt.plot(times, maxs, c='green')
    # plt.plot(times, mins, c='blue')
    # plt.xlabel('Hours')
    # plt.ylabel('Breaking Wave Height (ft)')
    # plt.grid(True)
    # plt.title('WaveWatch III: ' + ec_wave_model.latest_model_time().strftime('%d/%m/%Y %Hz'))
    # plt.show()

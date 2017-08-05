import wavemodel
import weathermodel
import tools
import units
import sys
from location import Location


if __name__=='__main__':
    ri_wave_location = Location(41.323, 360-71.396, alt=30.0, name='Block Island Sound')
    #ri_wind_location = Location()
    ec_wave_model = wavemodel.us_east_coast_wave_model()
    gfs_model = weathermodel.global_gfs_model()
    if ec_wave_model.fetch_ascii_data(ri_wave_location, 0, 60):
        data = ec_wave_model.to_buoy_data()
    else:
        print('Failed to fetch wave forecast data')
        sys.exit(0)

    if gfs_model.fetch_ascii_data(ri_wave_location, 0, 60):
        gfs_model.fill_buoy_data(data)
    else:
        print('Failed to fetch wind forecast data')
    
    for dat in data:
        dat.change_units(units.Units.english)
    json_data = tools.dump_json(data)
    with open('forecast.json', 'w') as outfile:
        outfile.write(json_data)

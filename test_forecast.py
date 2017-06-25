import wavemodel
import tools
import units
from location import Location


if __name__=='__main__':
    ri_wave_location = Location(41.323, 360-71.396, alt=30.0, name='Block Island Sound')
    ec_wave_model = wavemodel.us_east_coast_wave_model()
    if ec_wave_model.fetch_ascii_data(ri_wave_location, 0, 4):
        data = ec_wave_model.to_buoy_data()
        for dat in data:
            dat.change_units(units.Units.english)
        json_data = tools.dump_json(data)
        with open('forecast.json', 'w') as outfile:
            outfile.write(json_data)
    else:
        print('Failed to fetch forecast data')
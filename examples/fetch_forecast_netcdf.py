import sys
import matplotlib.pyplot as plt

import surfpy

if __name__=='__main__':
    ri_wave_location = surfpy.Location(41.4, -71.45, altitude=30.0, name='Block Island Sound')
    ri_wave_location.depth = 30.0
    ri_wave_location.angle = 145.0
    ri_wave_location.slope = 0.02
    ec_wave_model = surfpy.wavemodel.us_east_coast_wave_model_dense()

    print('Fetching WW3 Wave Data')
    model_dataset = ec_wave_model.fetch_netcdf_data()
    raw_wave_data = ec_wave_model.parse_netcdf_data(model_dataset, ri_wave_location, 0, 61)
    if raw_wave_data:
        data = ec_wave_model.to_buoy_data(raw_wave_data, surfpy.NOAAModel.DataMode.netcdf_mode)
    else:
        print('Failed to fetch wave forecast data')
        sys.exit(1)

    print('Fetching WW3 Weather Data')
    ri_wind_location = surfpy.Location(41.6, -71.5, altitude=10.0, name='Narragansett Pier')
    raw_weather_data = ec_wave_model.parse_netcdf_data(model_dataset, ri_wind_location, 0, 61)
    if raw_weather_data:
        ec_wave_model.fill_buoy_data(data, raw_weather_data, surfpy.NOAAModel.DataMode.netcdf_mode)
    else:
        print('Failed to fetch wind forecast data')
        #sys.exit(1)

    for dat in data:
        dat.solve_breaking_wave_heights(ri_wave_location)
        dat.change_units(surfpy.units.Units.english)
    json_data = surfpy.serialize(data)
    with open('forecast.json', 'w') as outfile:
        outfile.write(json_data)

    maxs =[x.maximum_breaking_height for x in data]
    mins = [x.minimum_breaking_height for x in data]
    summary = [x.wave_summary.wave_height for x in data]
    times = [x.date for x in data]

    plt.plot(times, maxs, c='green')
    plt.plot(times, mins, c='blue')
    plt.plot(times, summary, c='red')
    plt.xlabel('Hours')
    plt.ylabel('Breaking Wave Height (ft)')
    plt.grid(True)
    plt.title('WaveWatch III: ' + ec_wave_model.latest_model_time().strftime('%d/%m/%Y %Hz'))
    plt.show()

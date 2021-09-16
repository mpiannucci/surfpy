import sys
import matplotlib.pyplot as plt

import surfpy

if __name__=='__main__':
    ri_wave_location = surfpy.Location(41.35, -71.4, altitude=30.0, name='Rhode Island Coast')
    ri_wave_location.depth = 30.0
    ri_wave_location.angle = 145.0
    ri_wave_location.slope = 0.02
    atlantic_wave_model = surfpy.wavemodel.atlantic_gfs_wave_model()

    print('Fetching GFS Wave Data')
    num_hours_to_forecast = 24 # One day forecast. Change to 384 to get a 16 day forecast
    wave_grib_data = atlantic_wave_model.fetch_grib_datas(0, num_hours_to_forecast)
    raw_wave_data = atlantic_wave_model.parse_grib_datas(ri_wave_location, wave_grib_data)
    if raw_wave_data:
        data = atlantic_wave_model.to_buoy_data(raw_wave_data)
    else:
        print('Failed to fetch wave forecast data')
        sys.exit(1)

    print('Fetching local weather data')
    ri_wind_location = surfpy.Location(41.41, -71.45, altitude=0.0, name='Narragansett Pier')
    weather_data = surfpy.WeatherApi.fetch_hourly_forecast(ri_wind_location)
    surfpy.merge_wave_weather_data(data, weather_data)

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
    plt.title('GFS Wave Atlantic: ' + atlantic_wave_model.latest_model_time().strftime('%d/%m/%Y %Hz'))
    plt.show()
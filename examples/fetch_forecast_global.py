import sys
import matplotlib.pyplot as plt

import surfpy

if __name__=='__main__':
    # Set wave location
    wave_location = surfpy.Location(-22.942253, 14.412182, altitude=30.0, name='Skeleton Bay')
    wave_location.depth = 30.0
    wave_location.angle = 315.0
    wave_location.slope = 0.02
    global_wave_model = surfpy.wavemodel.global_gfs_wave_model_25km()

    print('Fetching GFS Wave Data')
    num_hours_to_forecast = 6 # 6 hour forecast. Change to 384 to get a 16 day forecast
    wave_grib_data = global_wave_model.fetch_grib_datas(0, num_hours_to_forecast, wave_location)
    raw_wave_data = global_wave_model.parse_grib_datas(wave_location, wave_grib_data)
    if raw_wave_data:
        data = global_wave_model.to_buoy_data(raw_wave_data)
    else:
        print('Failed to fetch wave forecast data')
        sys.exit(1)

    print('Fetching GFS Weather Data')
    global_weather_model = surfpy.weathermodel.global_gfs_weather_model()
    weather_grib_data = global_weather_model.fetch_grib_datas(0, num_hours_to_forecast, wave_location)
    raw_weather_data = global_weather_model.parse_grib_datas(wave_location, weather_grib_data)
    if raw_weather_data:
        weather_data = global_weather_model.to_buoy_data(raw_weather_data)
        
    else:
        print('Failed to fetch weather forecast data')
        sys.exit(1)

        
    surfpy.merge_wave_weather_data(data, weather_data)

    # Show breaking wave heights
    for dat in data:
        dat.solve_breaking_wave_heights(wave_location)
        dat.change_units(surfpy.units.Units.english)

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
    plt.title('GFS Wave Global: ' + global_wave_model.latest_model_time().strftime('%d/%m/%Y %Hz'))
    plt.show()

    # Show wind speed and direction over time
    wind_speeds = [x.wind_speed for x in data]
    wind_directions = [x.wind_direction for x in data]
    fig, ax1 = plt.subplots()

    # Wind speed (Primary Y-axis)
    ax1.plot(times, wind_speeds, 'b-', label="Wind Speed (mph)")
    ax1.set_xlabel('Time')
    ax1.set_ylabel('Wind Speed (mph)', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    # Wind direction (Secondary Y-axis)
    ax2 = ax1.twinx()
    ax2.plot(times, wind_directions, 'r-', label="Wind Direction (°)")
    ax2.set_ylabel('Wind Direction (°)', color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    # Add grid and title
    fig.suptitle('Wind Speed and Direction Over Time')
    ax1.grid(True)
    fig.tight_layout()

    plt.show()
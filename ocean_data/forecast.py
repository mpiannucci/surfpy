import datetime
import math
import surfpy
from surfpy.wavemodel import atlantic_gfs_wave_model
from surfpy.buoystation import BuoyStation
from surfpy.tidestation import TideStation
from surfpy.weatherapi import WeatherApi
from surfpy.location import Location
from ocean_data.location import get_spot_config

def get_surf_forecast(spot_name):
    """
    Orchestrates the fetching, merging, and processing of a 7-day surf forecast.

    Args:
        spot_name (str): The slug of the surf spot.

    Returns:
        list: A list of hourly forecast dictionaries, or None if the spot is invalid.
    """
    # 1. Get surf spot configuration
    spot_config = get_spot_config(spot_name)
    if not spot_config:
        return None

    # 2. Fetch all required data
    buoy_station = BuoyStation(station_id=spot_config['swell_buoy_id'], location=None)
    wave_model = atlantic_gfs_wave_model()
    wave_forecast = buoy_station.fetch_wave_forecast_bulletin(wave_model)

    tide_station = TideStation(station_id=spot_config['tide_station_id'], location=None)
    start_date = datetime.datetime.now(datetime.timezone.utc)
    end_date = start_date + datetime.timedelta(days=7)
    tide_data_result = tide_station.fetch_tide_data(start_date, end_date, interval='h', unit='english')
    hourly_tide_data = []
    if tide_data_result:
        _, hourly_tide_data = tide_data_result

    wind_location = Location(latitude=spot_config['wind_location']['lat'], longitude=spot_config['wind_location']['lon'])
    wind_forecast = WeatherApi.fetch_hourly_forecast(wind_location)

    # 3. Merge data into a single timeline
    merged_forecast = _merge_forecast_data(wave_forecast, hourly_tide_data, wind_forecast)

    # 4. Process the merged data (calculate breaking wave height)
    processed_forecast = _process_forecast(merged_forecast, spot_config['breaking_wave_params'])

    # 5. Format for API response
    return _format_for_api(processed_forecast)

def _merge_forecast_data(wave_data, tide_data, wind_data):
    """
    Merges wave, tide, and wind data into a single list of hourly dictionaries.
    It uses the wave forecast as the primary timeline and finds the closest
    tide and wind data point for each wave data point within a 1-hour tolerance.
    """
    merged = []
    if not wave_data:
        return merged

    for wave_entry in wave_data:
        # Find the closest tide data point
        closest_tide = None
        if tide_data:
            # Find the tide data point with the minimum time difference
            closest_tide = min(tide_data, key=lambda x: abs(x.date - wave_entry.date))
            
            # Ensure the closest data is within a reasonable time window (e.g., +/- 31 minutes)
            if abs(closest_tide.date - wave_entry.date) > datetime.timedelta(minutes=31):
                closest_tide = None

        # Find the closest wind data point
        closest_wind = None
        if wind_data:
            # Find the wind data point with the minimum time difference
            closest_wind = min(wind_data, key=lambda x: abs(x.date - wave_entry.date))

            # Ensure the closest data is within a reasonable time window (e.g., +/- 31 minutes)
            if abs(closest_wind.date - wave_entry.date) > datetime.timedelta(minutes=31):
                closest_wind = None
        
        merged.append({
            'wave': wave_entry,
            'tide': closest_tide,
            'wind': closest_wind
        })
        
    return merged

def _process_forecast(merged_data, breaking_wave_params):
    """Calculates breaking wave height and other derived data using the idiomatic library functions."""
    processed = []
    spot_location_details = Location(
        depth=breaking_wave_params['depth'],
        angle=breaking_wave_params['angle'],
        slope=breaking_wave_params['slope']
    )

    for hour_data in merged_data:
        wave = hour_data['wave']
        if not wave or not wave.swell_components:
            continue

        # Convert swell direction from "coming from" to "going toward"
        for component in wave.swell_components:
            if not math.isnan(component.direction):
                component.direction = (component.direction + 180) % 360
                component.compass_direction = surfpy.units.degree_to_direction(component.direction)

        wave.solve_breaking_wave_heights(spot_location_details)
        processed.append(hour_data)
        
    return processed

def _format_for_api(processed_data):
    """Formats the processed data into the final API JSON structure."""
    api_response = []
    for hour in processed_data:
        wave = hour['wave']
        tide = hour['tide']
        wind = hour['wind']

        swell_components = []
        if wave and wave.swell_components:
            for component in wave.swell_components:
                if not math.isnan(component.wave_height) and component.wave_height > 0:
                    swell_components.append({
                        "height": round(component.wave_height * 3.28084, 1),
                        "period": round(component.period, 1),
                        "direction": component.compass_direction,
                        "direction_degrees": int(component.direction) if not math.isnan(component.direction) else 0,
                        "unit": "ft"
                    })

        min_break = wave.minimum_breaking_height if wave and not math.isnan(wave.minimum_breaking_height) else 0.0
        max_break = wave.maximum_breaking_height if wave and not math.isnan(wave.maximum_breaking_height) else 0.0

        api_hour = {
            "timestamp": wave.date.strftime('%Y-%m-%dT%H:00:00Z') if wave else "N/A",
            "breaking_wave_height": {
                "min": round(min_break * 3.28084, 1),
                "max": round(max_break * 3.28084, 1),
                "unit": "ft"
            },
            "swell_components": swell_components,
            "wind": {
                "speed": wind.wind_speed if wind else 0,
                "direction": wind.wind_compass_direction if wind else "N/A",
                "unit": "mph"
            },
            "tide": {
                "height": round(tide.water_level, 1) if tide else 0,
                "unit": "ft"
            }
        }
        api_response.append(api_hour)
        
    return api_response
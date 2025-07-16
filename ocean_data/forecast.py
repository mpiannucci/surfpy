import datetime
import math
import surfpy
import pytz
from surfpy.wavemodel import atlantic_gfs_wave_model
from surfpy.buoystation import BuoyStation
from surfpy.tidestation import TideStation
from surfpy.weatherapi import WeatherApi
from surfpy.location import Location
from ocean_data.location import get_spot_config
from .swell import fetch_historical_swell_data
from .meteorology import fetch_historical_met_data
from .tide import fetch_historical_tide_data

def get_surf_forecast(spot_name):
    """
    Orchestrates fetching, merging, and processing a surf forecast that combines
    historical "actuals" with future "forecasts".
    """
    spot_config = get_spot_config(spot_name)
    if not spot_config:
        return None

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    historical_start_utc = now_utc - datetime.timedelta(hours=24)
    forecast_end_utc = now_utc + datetime.timedelta(days=7)

    # 1. Fetch Historical Data ("Actuals")
    actual_wave_data = fetch_historical_swell_data(spot_config['swell_buoy_id'], historical_start_utc, now_utc)
    actual_wind_data = fetch_historical_met_data(spot_config['swell_buoy_id'], historical_start_utc, now_utc)
    actual_tide_data = fetch_historical_tide_data(spot_config['tide_station_id'], historical_start_utc, now_utc)

    # 2. Fetch Forecast Data
    buoy_station = BuoyStation(station_id=spot_config['swell_buoy_id'], location=None)
    wave_model = atlantic_gfs_wave_model()
    forecast_generated_at = wave_model.latest_model_time().strftime('%Y-%m-%d %H:%M UTC')
    forecast_wave_data = buoy_station.fetch_wave_forecast_bulletin(wave_model) or []

    tide_station = TideStation(station_id=spot_config['tide_station_id'], location=None)
    tide_data_result = tide_station.fetch_tide_data(now_utc, forecast_end_utc, interval='h', unit='english')
    forecast_tide_data = []
    if tide_data_result:
        _, forecast_tide_data = tide_data_result

    wind_location = Location(latitude=spot_config['wind_location']['lat'], longitude=spot_config['wind_location']['lon'])
    forecast_wind_data = WeatherApi.fetch_hourly_forecast(wind_location) or []

    # 3. Tag and Combine Data
    # Helper function to combine actual and forecast data, prioritizing actuals
    def combine_data(actual_data, forecast_data):
        combined = {entry.date: entry for entry in forecast_data}
        for entry in actual_data:
            combined[entry.date] = entry  # Actuals overwrite forecasts for same timestamp
        return sorted(combined.values(), key=lambda x: x.date)

    all_wave_data = combine_data(actual_wave_data, forecast_wave_data)
    all_wind_data = combine_data(actual_wind_data, forecast_wind_data)
    all_tide_data = combine_data(actual_tide_data, forecast_tide_data)

    # Ensure all data points have a 'type' attribute
    for data in all_wave_data: data.type = 'actual' if data in actual_wave_data else 'forecast'
    for data in all_wind_data: data.type = 'actual' if data in actual_wind_data else 'forecast'
    for data in all_tide_data: data.type = 'actual' if data in actual_tide_data else 'forecast'

    # 4. Merge, Process, and Format
    merged_forecast = _merge_forecast_data(all_wave_data, all_tide_data, all_wind_data)
    processed_forecast = _process_forecast(merged_forecast, spot_config['breaking_wave_params'])
    formatted_api_response = _format_for_api(processed_forecast, spot_config.get('timezone'))

    return {
        "forecast_generated_at": forecast_generated_at,
        "timezone": spot_config.get('timezone', 'UTC'),
        "forecast_data": formatted_api_response
    }

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
        
        merged.append({
            'wave': wave_entry,
            'tide': closest_tide,
            'wind': closest_wind,
            'type': getattr(wave_entry, 'type', 'forecast')  # Carry over the type
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

def _format_for_api(processed_data, timezone_str='UTC'):
    """Formats the processed data into the final API JSON structure."""
    api_response = []
    
    # Get the timezone object, default to UTC if invalid
    try:
        local_tz = pytz.timezone(timezone_str)
    except pytz.UnknownTimeZoneError:
        local_tz = pytz.utc

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

        # Convert timestamp to local timezone
        utc_time = wave.date.replace(tzinfo=pytz.utc) if wave else datetime.datetime.now(pytz.utc)
        local_time = utc_time.astimezone(local_tz)

        api_hour = {
            "timestamp": local_time.isoformat(),
            "type": hour.get('type', 'forecast'),
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
                "height": round(tide.water_level * 3.28084, 1) if tide else 0,
                "unit": "ft"
            }
        }
        api_response.append(api_hour)
        
    return api_response
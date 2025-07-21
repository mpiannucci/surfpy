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
import requests

def _fetch_gfs_wave_bulletin(station_id, model_run_time):
    """
    Fetches and parses a GFS wave model bulletin for a specific model run time.
    Returns None if the bulletin is not available.
    """
    try:
        # Create a temporary buoy station to generate the URL and parse
        buoy_station = BuoyStation(station_id=station_id, location=None)

        # Manually construct the URL for the specific model_run_time
        model_run_str = str(model_run_time.hour).rjust(2, '0')
        date_str = model_run_time.strftime('%Y%m%d')
        # This URL structure is based on surfpy's BuoyStation logic
        url = f'https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.{date_str}/{model_run_str}/wave/station/bulls.t{model_run_str}z/gfswave.{station_id}.bull'
        
        response = requests.get(url, timeout=10) # Increased timeout for reliability
        if response.status_code != 200 or not response.text:
            print(f"Bulletin for {station_id} at {model_run_time} not found (status: {response.status_code}).")
            return None
        
        # Use the existing parser from surfpy
        return buoy_station.parse_wave_forecast_bulletin(response.text, None)
    except requests.exceptions.RequestException as e:
        print(f"Request failed for GFS bulletin at {model_run_time}: {e}")
        return None
    except Exception as e:
        print(f"An error occurred in _fetch_gfs_wave_bulletin: {e}")
        return None

def _find_closest_entry(data_list, target_datetime, max_minutes_diff=None):
    """
    Finds the data entry closest to the target_datetime within a data_list.
    Optionally, limits the search to a maximum time difference.
    """
    if not data_list:
        return None

    closest_entry = None
    min_diff = datetime.timedelta.max

    for entry in data_list:
        # Ensure entry.date is timezone-aware for comparison
        entry_date_utc = entry.date.replace(tzinfo=datetime.timezone.utc)
        diff = abs(entry_date_utc - target_datetime)

        if diff < min_diff:
            min_diff = diff
            closest_entry = entry

    if closest_entry and max_minutes_diff is not None:
        if min_diff > datetime.timedelta(minutes=max_minutes_diff):
            return None
            
    return closest_entry

def get_surf_forecast(spot_name):
    """
    Orchestrates fetching, merging, and processing a surf forecast that combines
    historical "actuals" with future "forecasts".
    """
    spot_config = get_spot_config(spot_name)
    if not spot_config:
        return None

    now_utc = datetime.datetime.now(datetime.timezone.utc)
    handoff_hour_utc = now_utc.replace(minute=0, second=0, microsecond=0)
    historical_start_utc = handoff_hour_utc - datetime.timedelta(hours=24)
    forecast_end_utc = handoff_hour_utc + datetime.timedelta(days=7)

    # Generate hourly grid for actuals (last 24 hours up to current hour)
    hourly_grid_actuals = []
    for i in range(24, 0, -1):
        hourly_grid_actuals.append(handoff_hour_utc - datetime.timedelta(hours=i))
    hourly_grid_actuals.append(handoff_hour_utc) # Include the handoff hour itself

    # Generate hourly grid for forecasts (from next hour for 7 days)
    hourly_grid_forecasts = []
    for i in range(1, 7 * 24 + 1):
        hourly_grid_forecasts.append(handoff_hour_utc + datetime.timedelta(hours=i))

    # 1. Fetch Historical Data ("Actuals")
    actual_wave_data = fetch_historical_swell_data(spot_config['swell_buoy_id'], historical_start_utc, now_utc)
    actual_wind_data = fetch_historical_met_data(spot_config.get('met_buoy_id', spot_config['swell_buoy_id']), historical_start_utc, now_utc)
    actual_tide_data = fetch_historical_tide_data(spot_config['tide_station_id'], historical_start_utc, now_utc)

    # 2. Fetch Forecast Data
    wave_model = atlantic_gfs_wave_model()
    latest_run_time = wave_model.latest_model_time()

    # Attempt to fetch the latest forecast, with a fallback to the previous run
    forecast_wave_data = _fetch_gfs_wave_bulletin(spot_config['swell_buoy_id'], latest_run_time)
    if forecast_wave_data:
        forecast_generated_at = latest_run_time.strftime('%Y-%m-%d %H:%M UTC')
    else:
        print(f"Latest forecast not available. Falling back to previous model run.")
        previous_run_time = latest_run_time - datetime.timedelta(hours=6)
        forecast_wave_data = _fetch_gfs_wave_bulletin(spot_config['swell_buoy_id'], previous_run_time)
        if forecast_wave_data:
            forecast_generated_at = previous_run_time.strftime('%Y-%m-%d %H:%M UTC')
        else:
            print(f"Fallback forecast also failed. No wave forecast data available.")
            forecast_wave_data = []
            forecast_generated_at = "N/A"

    tide_station = TideStation(station_id=spot_config['tide_station_id'], location=None)
    tide_data_result = tide_station.fetch_tide_data(now_utc, forecast_end_utc, interval='h', unit='metric')
    forecast_tide_data = []
    if tide_data_result:
        _, forecast_tide_data = tide_data_result

    wind_location = Location(latitude=spot_config['wind_location']['lat'], longitude=spot_config['wind_location']['lon'])
    forecast_wind_data = WeatherApi.fetch_hourly_forecast(wind_location) or []

    # 3. Implement Resampling Loop
    resampled_forecast_data = []

    # Process actuals
    for grid_hour in hourly_grid_actuals:
        wave_entry = _find_closest_entry(actual_wave_data, grid_hour, max_minutes_diff=30)
        wind_entry = _find_closest_entry(actual_wind_data, grid_hour, max_minutes_diff=30)
        tide_entry = _find_closest_entry(actual_tide_data, grid_hour, max_minutes_diff=30)

        # Only add if at least wave data is present for the hour
        if wave_entry:
            resampled_forecast_data.append({
                'wave': wave_entry,
                'wind': wind_entry,
                'tide': tide_entry,
                'type': 'actual',
                'grid_hour': grid_hour # Add grid_hour here
            })

    # Process forecasts
    for grid_hour in hourly_grid_forecasts:
        wave_entry = _find_closest_entry(forecast_wave_data, grid_hour)
        wind_entry = _find_closest_entry(forecast_wind_data, grid_hour)
        tide_entry = _find_closest_entry(forecast_tide_data, grid_hour)

        # Only add if at least wave data is present for the hour
        if wave_entry:
            resampled_forecast_data.append({
                'wave': wave_entry,
                'wind': wind_entry,
                'tide': tide_entry,
                'type': 'forecast',
                'grid_hour': grid_hour # Add grid_hour here
            })

    # 4. Process, and Format
    processed_forecast = _process_forecast(resampled_forecast_data, spot_config['breaking_wave_params'])
    formatted_api_response = _format_for_api(processed_forecast, spot_config.get('timezone'))

    return {
        "forecast_generated_at": forecast_generated_at,
        "timezone": spot_config.get('timezone', 'UTC'),
        "forecast_data": formatted_api_response
    }

def _process_forecast(resampled_data, breaking_wave_params):
    """Calculates breaking wave height and other derived data using the idiomatic library functions."""
    processed = []
    spot_location_details = Location(
        depth=breaking_wave_params['depth'],
        angle=breaking_wave_params['angle'],
        slope=breaking_wave_params['slope']
    )

    for hour_data in resampled_data:
        wave = hour_data['wave']
        if not wave or not wave.swell_components:
            # If no wave data for this hour, skip or append a placeholder
            processed.append(hour_data) # Append as is, _format_for_api will handle missing data
            continue

        # Convert swell direction from "coming from" to "going toward" for FORECAST data only
        for component in wave.swell_components:
            if not math.isnan(component.direction):
                if hour_data['type'] == 'forecast':
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

    for hour_data in processed_data:
        wave = hour_data.get('wave')
        tide = hour_data.get('tide')
        wind = hour_data.get('wind')

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

        # Breaking Wave Height Logic
        min_break_ft = (wave.minimum_breaking_height * 3.28084) if wave and not math.isnan(wave.minimum_breaking_height) else 0.0
        max_break_ft = (wave.maximum_breaking_height * 3.28084) if wave and not math.isnan(wave.maximum_breaking_height) else 0.0

        rounded_min = round(min_break_ft)
        rounded_max = round(max_break_ft)

        range_text = ""
        if rounded_max <= 0:
            range_text = "Flat"
            # Ensure max is also 0 for consistency in the JSON
            json_max = 0
        else:
            final_min = rounded_min
            if rounded_min >= rounded_max:
                final_min = rounded_max - 1
            
            # Ensure the floor is 0
            if final_min < 0:
                final_min = 0
            
            range_text = f"{final_min}-{rounded_max} ft"
            json_max = rounded_max

        breaking_wave_height_json = {
            "max": json_max,
            "range_text": range_text,
            "unit": "ft"
        }

        # Convert timestamp to local timezone
        utc_time = hour_data['grid_hour'].replace(tzinfo=pytz.utc)
        local_time = utc_time.astimezone(local_tz)

        # Handle wind speed conversion to knots
        wind_speed_knots = 0
        wind_direction = "N/A"
        wind_direction_degrees = 0
        if wind:
            if wind.unit == surfpy.units.Units.metric:
                # Convert from m/s to knots
                wind_speed_knots = surfpy.units.convert(wind.wind_speed, surfpy.units.Measurement.speed, surfpy.units.Units.metric, surfpy.units.Units.knots)
            elif wind.unit == surfpy.units.Units.english:
                # Convert from mph to knots
                wind_speed_knots = surfpy.units.convert(wind.wind_speed, surfpy.units.Measurement.speed, surfpy.units.Units.english, surfpy.units.Units.knots)
            else:
                # Should not happen, but as a fallback
                wind_speed_knots = wind.wind_speed
            
            wind_direction = wind.wind_compass_direction
            if hasattr(wind, 'wind_direction') and not math.isnan(wind.wind_direction):
                wind_direction_degrees = int(wind.wind_direction)

        api_hour = {
            "timestamp": local_time.isoformat(),
            "type": hour_data.get('type', 'forecast'),
            "breaking_wave_height": breaking_wave_height_json,
            "swell_components": swell_components,
            "wind": {
                "speed": round(wind_speed_knots, 1) if wind else 0,
                "direction": wind_direction if wind else "N/A",
                "direction_degrees": wind_direction_degrees,
                "unit": "knots"
            },
            "tide": {
                "height": round(tide.water_level * 3.28084, 1) if tide else 0,
                "unit": "ft"
            }
        }
        api_response.append(api_hour)
        
    return api_response
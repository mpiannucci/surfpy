from datetime import datetime, timezone
import surfpy
import json
import argparse
import sys

def find_closest_buoy(latitude, longitude, active=True):
    """Find the closest buoy to a given location."""
    location = surfpy.Location(latitude, longitude)
    
    stations = surfpy.BuoyStations()
    stations.fetch_stations()
    
    # Find closest active buoy
    closest_buoy = stations.find_closest_buoy(
        location, 
        active=active,
        buoy_type=surfpy.BuoyStation.BuoyType.buoy
    )
    
    return closest_buoy

def fetch_swell_data(buoy, count=500):
    """Fetch wave data for a given buoy."""
    if not buoy:
        return None
    
    try:
        # Try wave spectra reading first
        wave_data = buoy.fetch_wave_spectra_reading(count)
        
        if not wave_data:
            # Try fetch_latest_reading as an alternative
            latest_data = buoy.fetch_latest_reading()
            
            if latest_data:
                # Return as a list with one item for consistent processing
                return [latest_data]
                
            # Try fetch_wave_energy_reading
            try:
                wave_data = buoy.fetch_wave_energy_reading(count)
                return wave_data
            except AttributeError:
                return None
                
        return wave_data
    except Exception as e:
        print(f"Error fetching wave data: {str(e)}")
        return None

def find_closest_data(data_list, target_datetime):
    """Find the data entry closest to the given target datetime."""
    if not data_list:
        return None
    return min(data_list, key=lambda entry: abs(entry.date.replace(tzinfo=timezone.utc) - target_datetime))

def swell_data_to_json(wave_data, buoy=None):
    """Convert swell data to a JSON-serializable structure."""
    METERS_TO_FEET = 3.28084
    wave_json = []
    if wave_data:
        for entry in wave_data:
            data_point = {"date": entry.date.isoformat() if hasattr(entry, 'date') else datetime.now().isoformat()}
            
            # Handle wave spectra data (with swell components)
            if hasattr(entry, 'swell_components') and entry.swell_components:
                swell_data = {}
                for i, swell in enumerate(entry.swell_components):
                    swell_info = {}
                    if hasattr(swell, 'wave_height'):
                        swell_info['height'] = round(swell.wave_height * METERS_TO_FEET, 1)
                    if hasattr(swell, 'period'):
                        swell_info['period'] = swell.period
                    if hasattr(swell, 'direction'):
                        swell_info['direction'] = swell.direction
                    
                    swell_data[f"swell_{i+1}"] = swell_info
                
                data_point["swell_components"] = swell_data
            
            # Handle generic wave attributes
            for attr in ['wave_height', 'period', 'average_period', 'direction', 
                         'steepness', 'average_wave_period', 'dominant_wave_period',
                         'significant_wave_height', 'swell_height', 'swell_period', 
                         'wind_wave_height', 'wind_wave_period', 'wind_wave_direction']:
                if hasattr(entry, attr):
                    value = getattr(entry, attr)
                    if value is not None:
                        # Convert any height attributes from meters to feet
                        if 'height' in attr and value is not None:
                            value = round(value * METERS_TO_FEET, 1)
                        data_point[attr] = value
            
            wave_json.append(data_point)
    
    result = {"wave_data": wave_json}
    
    # Add buoy info if available
    if buoy:
        result["buoy_info"] = {
            "id": buoy.station_id,
            "location": {
                "latitude": buoy.location.latitude,
                "longitude": buoy.location.longitude
            }
        }
    
    return result

def main(latitude, longitude, timestamp=None):
    """
    Main function that takes a location and finds closest buoy.
   
    Args:
        latitude (float): Latitude coordinate
        longitude (float): Longitude coordinate
        timestamp (str, optional): ISO format timestamp (e.g., "2023-10-01T12:00:00")
                                   Defaults to current time if None.
    """
    if timestamp:
        try:
            target_datetime = datetime.fromisoformat(timestamp).replace(tzinfo=timezone.utc)
            print(f"Using specified timestamp: {target_datetime}")
        except ValueError:
            print(f"Invalid timestamp format: {timestamp}. Using current time instead.")
            target_datetime = datetime.now(timezone.utc)
    else:
        target_datetime = datetime.now(timezone.utc)
        print(f"Using current time: {target_datetime}")
    
    count = 1100
    
    print(f"Finding closest buoy to location: {latitude}, {longitude}")
    closest_buoy = find_closest_buoy(latitude, longitude)
    
    if not closest_buoy:
        return {"error": "Could not find any active buoys"}
    
    print(f"Found closest buoy: {closest_buoy.station_id} at location: {closest_buoy.location.latitude}, {closest_buoy.location.longitude}")
    
    # Try to get wave data
    wave_data = fetch_swell_data(closest_buoy, count)
    
    if not wave_data:
        # Try to find another nearby buoy
        print("Searching for another nearby buoy with wave data...")
        location = surfpy.Location(latitude, longitude)
        stations = surfpy.BuoyStations()
        stations.fetch_stations()
        
        # Get all stations sorted by distance
        nearby_stations = sorted(
            stations.stations, 
            key=lambda s: s.location.distance(location)
        )
        
        # Skip the first one (it's the closest one we already tried)
        for station in nearby_stations[1:5]:  # Try the next 4 closest buoys
            print(f"Trying buoy {station.station_id}...")
            wave_data = fetch_swell_data(station, count)
            if wave_data:
                closest_buoy = station
                break
    
    if not wave_data:
        return {"error": "No wave data found for any nearby buoys"}
    
    closest_wave = find_closest_data(wave_data, target_datetime)
    
    result = swell_data_to_json([closest_wave] if closest_wave else [], closest_buoy)
    return result

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get swell data for a location')
    parser.add_argument('latitude', type=float, help='Latitude coordinate')
    parser.add_argument('longitude', type=float, help='Longitude coordinate')
    parser.add_argument('--timestamp', '-t', help='ISO format timestamp (e.g., "2023-10-01T12:00:00")')
    
    if len(sys.argv) >= 3:
        args = parser.parse_args()

        result = main(args.latitude, args.longitude, args.timestamp)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python get_swell.py LATITUDE LONGITUDE [--timestamp TIMESTAMP]")
        print("Example: python get_swell.py 36.6 -122.0")
        print("Example with timestamp: python get_swell.py 36.6 -122.0 --timestamp 2023-10-01T12:00:00")
        sys.exit(1)
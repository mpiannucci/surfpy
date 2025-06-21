#!/usr/bin/env python3
"""
Test script for meteorology.py module

This script allows you to test the meteorological data functionality
from the command line using surf spot names (which get mapped to buoys).

Usage:
    python test_meteorology.py --spot lido --date "2025-06-20" --time "14:00:00"
    python test_meteorology.py --spot manasquan  # Uses current time
    python test_meteorology.py --list-spots     # Show available surf spots
    python test_meteorology.py --buoy 44009     # Direct buoy testing (fallback)
"""

import argparse
import json
from datetime import datetime, timezone
import pytz
import sys
import os

# Add the parent directory to the path so we can import the ocean_data module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ocean_data.meteorology import fetch_meteorological_data, fetch_met_buoy
    from ocean_data.location import (
        get_buoys_for_location, 
        get_all_locations, 
        is_valid_location,
        get_location_info,
        LOCATION_TO_BUOYS
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running this from the correct directory and the ocean_data module is available.")
    sys.exit(1)

def list_available_spots():
    """Display all available surf spots and their associated buoys."""
    print("\n=== Available Surf Spots ===")
    locations = get_all_locations()
    
    for location in sorted(locations):
        buoys = get_buoys_for_location(location)
        location_info = get_location_info(location)
        
        print(f"\nSpot: {location.upper()}")
        if location_info and location_info.get('coordinates'):
            coords = location_info['coordinates']
            print(f"  Coordinates: {coords['lat']:.4f}, {coords['lon']:.4f}")
        
        print(f"  Meteorological Buoy: {buoys['met']}")
        print(f"  Swell Buoy: {buoys['swell']}")
        print(f"  Tide Station: {buoys['tide']}")

def validate_surf_spot(spot_name):
    """Validate and get buoy information for a surf spot."""
    print(f"\n=== Validating Surf Spot: {spot_name} ===")
    
    if not is_valid_location(spot_name):
        print(f"✗ '{spot_name}' is not a valid surf spot")
        print(f"Available spots: {', '.join(get_all_locations())}")
        return None
    
    buoys = get_buoys_for_location(spot_name)
    location_info = get_location_info(spot_name)
    
    print(f"✓ Valid surf spot: {spot_name.upper()}")
    if location_info and location_info.get('coordinates'):
        coords = location_info['coordinates']
        print(f"  Location: {coords['lat']:.4f}°N, {coords['lon']:.4f}°W")
    
    print(f"  Will use meteorological buoy: {buoys['met']}")
    
    return buoys['met']

def test_buoy_connection(buoy_id, spot_name=None):
    """Test if we can connect to and retrieve a specific buoy."""
    spot_info = f" (from {spot_name.upper()})" if spot_name else ""
    print(f"\n=== Testing Buoy Connection: {buoy_id}{spot_info} ===")
    
    buoy = fetch_met_buoy(buoy_id)
    if buoy:
        print(f"✓ Successfully connected to buoy {buoy_id}")
        print(f"  Station Name: {getattr(buoy, 'station_name', 'Unknown')}")
        print(f"  Location: {getattr(buoy, 'location', 'Unknown')}")
    else:
        print(f"✗ Failed to connect to buoy {buoy_id}")
        return False
    return True

def test_meteorological_data(buoy_id, target_datetime, count=50, spot_name=None):
    """Test fetching meteorological data for a specific buoy and time."""
    spot_info = f" for {spot_name.upper()}" if spot_name else ""
    print(f"\n=== Testing Meteorological Data Retrieval{spot_info} ===")
    print(f"Buoy ID: {buoy_id}")
    print(f"Target Time: {target_datetime}")
    print(f"Data Points to Fetch: {count}")
    
    try:
        met_data = fetch_meteorological_data(buoy_id, target_datetime, count)
        
        if met_data:
            print(f"✓ Successfully retrieved meteorological data")
            print(f"  Number of data points: {len(met_data)}")
            
            # Display the first data point
            if met_data:
                first_point = met_data[0]
                print(f"\n=== Sample Data Point ===")
                for key, value in first_point.items():
                    if key == 'date':
                        # Parse and display in a nicer format
                        try:
                            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                            eastern = pytz.timezone('America/New_York')
                            eastern_time = dt.astimezone(eastern)
                            print(f"  {key}: {eastern_time.strftime('%Y-%m-%d %H:%M:%S %Z')} (UTC: {dt.strftime('%H:%M:%S')})")
                        except:
                            print(f"  {key}: {value}")
                    else:
                        unit_map = {
                            'wind_speed': 'kts',
                            'wind_gust': 'kts', 
                            'wind_direction': '°',
                            'air_temperature': '°F',
                            'water_temperature': '°F',
                            'pressure': 'hPa',
                            'dewpoint_temperature': '°F'
                        }
                        unit = unit_map.get(key, '')
                        print(f"  {key}: {value} {unit}")
                        
                return met_data
        else:
            print("✗ No meteorological data retrieved")
            return None
            
    except Exception as e:
        print(f"✗ Error retrieving meteorological data: {e}")
        import traceback
        traceback.print_exc()
        return None

def parse_datetime(date_str, time_str=None):
    """Parse date and time strings into a timezone-aware datetime object."""
    try:
        if time_str:
            datetime_str = f"{date_str}T{time_str}"
        else:
            datetime_str = date_str
            
        # Parse as naive datetime
        naive_dt = datetime.fromisoformat(datetime_str)
        
        # Convert to Eastern Time (matching your app's timezone handling)
        eastern = pytz.timezone('America/New_York')
        localized_dt = eastern.localize(naive_dt)
        
        # Convert to UTC for data retrieval
        utc_dt = localized_dt.astimezone(timezone.utc)
        
        print(f"Input time (Eastern): {localized_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"Converted to UTC: {utc_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        return utc_dt
        
    except Exception as e:
        print(f"Error parsing datetime: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Test meteorological data functionality by surf spot')
    parser.add_argument('--spot', type=str, help='Surf spot name (e.g., lido, manasquan, rockaways)')
    parser.add_argument('--buoy', type=str, help='Direct buoy ID to test (fallback option)')
    parser.add_argument('--date', type=str, help='Date in YYYY-MM-DD format')
    parser.add_argument('--time', type=str, help='Time in HH:MM:SS format')
    parser.add_argument('--count', type=int, default=50, help='Number of data points to fetch (default: 50)')
    parser.add_argument('--list-spots', action='store_true', help='List available surf spots')
    parser.add_argument('--output', type=str, help='Save output to JSON file')
    
    args = parser.parse_args()
    
    # Show available spots if requested
    if args.list_spots:
        list_available_spots()
        if not args.spot and not args.buoy:
            return
    
    # Determine buoy ID and spot name
    buoy_id = None
    spot_name = None
    
    if args.spot:
        # Use surf spot to lookup buoy
        spot_name = args.spot.lower()
        buoy_id = validate_surf_spot(spot_name)
        if not buoy_id:
            return
    elif args.buoy:
        # Direct buoy specification
        buoy_id = args.buoy
        print(f"\nUsing direct buoy specification: {buoy_id}")
    else:
        # Default to Lido Beach
        spot_name = "lido"
        buoy_id = validate_surf_spot(spot_name)
        print(f"No spot specified. Using default: {spot_name.upper()}")
    
    # Parse datetime
    if args.date:
        target_datetime = parse_datetime(args.date, args.time)
        if not target_datetime:
            print("Failed to parse datetime. Exiting.")
            return
    else:
        # Use current time if no date specified
        target_datetime = datetime.now(timezone.utc)
        eastern = pytz.timezone('America/New_York')
        eastern_time = target_datetime.astimezone(eastern)
        print(f"No date specified. Using current time: {eastern_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    print(f"\n{'='*60}")
    print(f"METEOROLOGICAL DATA TEST")
    if spot_name:
        print(f"Surf Spot: {spot_name.upper()}")
    print(f"Buoy ID: {buoy_id}")
    print(f"{'='*60}")
    
    # Test buoy connection
    if not test_buoy_connection(buoy_id, spot_name):
        print("Buoy connection failed. Exiting.")
        return
    
    # Test meteorological data retrieval
    met_data = test_meteorological_data(buoy_id, target_datetime, args.count, spot_name)
    
    # Save output if requested
    if args.output and met_data:
        try:
            output_data = {
                "surf_spot": spot_name,
                "buoy_id": buoy_id,
                "target_datetime": target_datetime.isoformat(),
                "data_points": len(met_data),
                "meteorological_data": met_data
            }
            
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"\n✓ Data saved to {args.output}")
        except Exception as e:
            print(f"✗ Error saving data: {e}")
    
    print(f"\n{'='*60}")
    print("Test completed!")
    
    # Suggest other spots to try
    if spot_name:
        other_spots = [s for s in get_all_locations() if s != spot_name]
        if other_spots:
            print(f"\nTry other spots: {', '.join(other_spots[:3])}")

if __name__ == "__main__":
    main()
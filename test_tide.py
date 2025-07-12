#!/usr/bin/env python3
"""
Simplified test script for tide.py module - focuses on data tracing

Usage:
    python test_tide_simple.py --spot lido --date "2025-06-20" --time "14:00:00"
    python test_tide_simple.py --spot manasquan
    python test_tide_simple.py --list-spots
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
    from ocean_data.tide import fetch_tide_data
    from ocean_data.location import (
        get_buoys_for_location, 
        get_all_locations, 
        is_valid_location
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def list_available_spots():
    """Display available surf spots and their tide stations."""
    print("Available surf spots:")
    for location in sorted(get_all_locations()):
        buoys = get_buoys_for_location(location)
        print(f"  {location.upper()}: tide station {buoys['tide']}")

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
        
        return utc_dt, localized_dt
        
    except Exception as e:
        print(f"Error parsing datetime: {e}")
        return None, None

def test_tide_spot(spot_name, target_datetime_utc, target_datetime_eastern):
    """Test tide data for a specific spot."""
    print(f"\n{'='*50}")
    print(f"TIDE DATA TEST: {spot_name.upper()}")
    print(f"{'='*50}")
    
    # Get tide station for the spot
    if not is_valid_location(spot_name):
        print(f"❌ Invalid surf spot: {spot_name}")
        return None
        
    buoys = get_buoys_for_location(spot_name)
    station_id = buoys['tide']
    
    print(f"Tide station: {station_id}")
    print(f"Target time (Eastern): {target_datetime_eastern.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Target time (UTC): {target_datetime_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print()
    
    # Fetch tide data
    print("Fetching tide data...")
    tide_data = fetch_tide_data(station_id, target_datetime_utc, use_imperial_units=True)
    
    if tide_data:
        print(f"✅ Success! Retrieved tide data:")
        print(f"   Water level: {tide_data.get('water_level')} {tide_data.get('units')}")
        
        # Parse the returned date for comparison
        try:
            returned_date_str = tide_data.get('date', '')
            if returned_date_str:
                returned_date = datetime.fromisoformat(returned_date_str.replace('Z', '+00:00'))
                returned_eastern = returned_date.astimezone(pytz.timezone('America/New_York'))
                
                # Calculate time difference
                time_diff = abs(returned_date - target_datetime_utc)
                minutes_diff = time_diff.total_seconds() / 60
                
                print(f"   Data timestamp (Eastern): {returned_eastern.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                print(f"   Data timestamp (UTC): {returned_date.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                print(f"   Time difference: {minutes_diff:.1f} minutes")
                
                if minutes_diff > 30:
                    print(f"   ⚠️  Warning: Data is {minutes_diff:.1f} minutes away from target time")
                else:
                    print(f"   ✅ Good: Data is close to target time")
        except Exception as e:
            print(f"   ❌ Error parsing returned date: {e}")
            
        return tide_data
    else:
        print("❌ Failed to retrieve tide data")
        return None

def main():
    parser = argparse.ArgumentParser(description='Simple tide data test')
    parser.add_argument('--spot', type=str, help='Surf spot name')
    parser.add_argument('--date', type=str, help='Date in YYYY-MM-DD format')
    parser.add_argument('--time', type=str, help='Time in HH:MM:SS format') 
    parser.add_argument('--list-spots', action='store_true', help='List available surf spots')
    parser.add_argument('--output', type=str, help='Save output to JSON file')
    
    args = parser.parse_args()
    
    if args.list_spots:
        list_available_spots()
        if not args.spot:
            return
    
    # Determine spot
    spot_name = args.spot.lower() if args.spot else "lido"
    
    # Parse datetime
    if args.date:
        target_datetime_utc, target_datetime_eastern = parse_datetime(args.date, args.time)
        if not target_datetime_utc:
            print("Failed to parse datetime. Exiting.")
            return
    else:
        # Use current time
        target_datetime_utc = datetime.now(timezone.utc)
        eastern = pytz.timezone('America/New_York')
        target_datetime_eastern = target_datetime_utc.astimezone(eastern)
        print(f"No date specified. Using current time.")
    
    # Test tide data
    tide_data = test_tide_spot(spot_name, target_datetime_utc, target_datetime_eastern)
    
    # Save output if requested
    if args.output and tide_data:
        try:
            output_data = {
                "surf_spot": spot_name,
                "target_datetime_utc": target_datetime_utc.isoformat(),
                "target_datetime_eastern": target_datetime_eastern.isoformat(),
                "tide_data": tide_data
            }
            
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"\n💾 Data saved to {args.output}")
        except Exception as e:
            print(f"❌ Error saving data: {e}")

if __name__ == "__main__":
    main()
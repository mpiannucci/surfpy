# collect_ndbc_data.py
import sys
import json
import sqlite3
from datetime import datetime, timezone, timedelta
import pytz

# Import from ocean_data
from ocean_data import swell, location, utils

def collect_data_for_location(loc_name, date_obj):
    """
    Collect NDBC buoy data for a specific location and date.
    
    Args:
        loc_name (str): Location name (e.g., 'lido')
        date_obj (datetime.date): Date to collect data for (in Eastern Time)
        
    Returns:
        list: Processed data points
    """
    # Get buoy information for location
    buoy_info = location.get_buoys_for_location(loc_name)
    if not buoy_info:
        print(f"Unknown location: {loc_name}")
        return []
    
    print(f"Buoy info for {loc_name}: {buoy_info}")
    swell_buoy_id = buoy_info["swell"]
    
    # Create datetime range for the day (in Eastern Time)
    eastern = pytz.timezone('America/New_York')
    
    # Start and end of the requested date in Eastern Time
    # Add a buffer of 1 hour before and after to catch readings near the boundaries
    start_of_day_eastern = eastern.localize(datetime.combine(date_obj, datetime.min.time())) - timedelta(hours=1)
    end_of_day_eastern = eastern.localize(datetime.combine(date_obj, datetime.max.time())) + timedelta(hours=1)
    
    # Convert to UTC for API calls
    start_utc = start_of_day_eastern.astimezone(pytz.UTC)
    end_utc = end_of_day_eastern.astimezone(pytz.UTC)
    
    print(f"Fetching swell data for buoy {swell_buoy_id} from {start_utc} to {end_utc}")
    
    # Fetch swell data for this period
    swell_data = swell.fetch_swell_data(swell_buoy_id, start_utc, count=500)
    
    print(f"Received {len(swell_data) if swell_data else 0} swell data entries")
    
    if not swell_data:
        print(f"No swell data found for {loc_name} on {date_obj}")
        return []
    
    # Show a sample of the data
    print(f"Sample data entry: {json.dumps(swell_data[0], indent=2) if swell_data else 'None'}")
    
    # Process the data
    processed_data = []
    for i, entry in enumerate(swell_data):
        # Parse the buoy data structure from swell.py into our database format
        print(f"Processing entry {i+1}/{len(swell_data)}")
        
        # Extract timestamp - handle both string and datetime formats
        if 'date' in entry:
            if isinstance(entry['date'], str):
                try:
                    entry_time = datetime.fromisoformat(entry['date'])
                    if entry_time.tzinfo is None:
                        entry_time = entry_time.replace(tzinfo=timezone.utc)
                    print(f"Parsed date string: {entry['date']} to {entry_time}")
                except ValueError:
                    print(f"Could not parse date string: {entry['date']}")
                    continue
            else:
                entry_time = utils.convert_to_utc(entry['date'])
                print(f"Converted datetime object: {entry['date']} to {entry_time}")
        else:
            print("Entry missing date field, skipping")
            continue
        
        # Convert to Eastern time for date comparison
        entry_time_eastern = entry_time.astimezone(eastern)
        entry_date_eastern = entry_time_eastern.date()
        
        # Check if the Eastern date matches our target date
        if entry_date_eastern != date_obj:
            print(f"Entry date in Eastern time {entry_date_eastern} doesn't match target date {date_obj}, skipping")
            continue
        
        # Proceed with processing the data point since it's for our target date
        data_point = {
            "timestamp": entry_time,
            "significant_height": entry.get("significant_wave_height")
        }
        
        # Get swell components
        if 'swell_components' in entry:
            components = entry['swell_components']
            print(f"Found {len(components)} swell components")
            
            # Primary swell
            if 'swell_1' in components:
                primary = components['swell_1']
                data_point["primary_swell_height"] = primary.get('height')
                data_point["primary_swell_period"] = primary.get('period')
                data_point["primary_swell_direction"] = primary.get('direction')
                print(f"Primary swell: {primary}")
            
            # Secondary swell
            if 'swell_2' in components:
                secondary = components['swell_2']
                data_point["secondary_swell_height"] = secondary.get('height')
                data_point["secondary_swell_period"] = secondary.get('period')
                data_point["secondary_swell_direction"] = secondary.get('direction')
                print(f"Secondary swell: {secondary}")
        else:
            print("No swell components found in entry")
        
        # Store raw data
        data_point["raw_data"] = json.dumps(entry)
        
        processed_data.append(data_point)
        print(f"Added data point: {data_point}")
    
    print(f"Processed {len(processed_data)} data points for {loc_name} on {date_obj}")
    return processed_data

def save_to_database(location_name, data, buoy_id):
    """Save processed data to the SQLite database."""
    if not data:
        print("No data to save")
        return
    
    conn = sqlite3.connect('swell_data.db')
    cursor = conn.cursor()
    
    for entry in data:
        cursor.execute('''
        INSERT INTO swell_readings (
            source, location, buoy_id, timestamp, 
            significant_height, primary_swell_height, primary_swell_period, primary_swell_direction,
            secondary_swell_height, secondary_swell_period, secondary_swell_direction,
            raw_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'ndbc_buoy', 
            location_name, 
            buoy_id, 
            entry["timestamp"].isoformat(),
            entry.get("significant_height"),
            entry.get("primary_swell_height"),
            entry.get("primary_swell_period"),
            entry.get("primary_swell_direction"),
            entry.get("secondary_swell_height"),
            entry.get("secondary_swell_period"),
            entry.get("secondary_swell_direction"),
            entry.get("raw_data")
        ))
    
    conn.commit()
    print(f"Saved {len(data)} NDBC buoy readings to database")
    conn.close()

def main():
    # Check command line arguments
    if len(sys.argv) < 3:
        print("Usage: python collect_ndbc_data.py <location> <date>")
        print("Example: python collect_ndbc_data.py lido 2025-05-19")
        return
    
    # Use a different variable name to avoid conflict with the imported module
    loc_name = sys.argv[1]
    date_str = sys.argv[2]
    
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD")
        return
    
    # Get buoy information for location
    buoy_mapping = location.get_buoys_for_location(loc_name)
    if not buoy_mapping:
        print(f"Unknown location: {loc_name}")
        return
    
    buoy_id = buoy_mapping["swell"]
    
    # Collect and process data
    processed_data = collect_data_for_location(loc_name, date_obj)
    
    # Save to database
    if processed_data:
        save_to_database(loc_name, processed_data, buoy_id)
    else:
        print(f"No data to save for {loc_name} on {date_obj}")

if __name__ == "__main__":
    main()
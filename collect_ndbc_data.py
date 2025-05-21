# collect_ndbc_data.py
import sys
import json
import sqlite3
from datetime import datetime, timezone, timedelta
import pytz

# Import from ocean_data
from ocean_data import swell, location, utils

def setup_database():
    """Create the database schema if it doesn't exist."""
    conn = sqlite3.connect('swell_data.db')
    cursor = conn.cursor()
    
    # Main table for all swell readings
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS swell_readings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,                      -- 'surfline_lotus', 'surfline_buoy', or 'ndbc_buoy'
        location TEXT NOT NULL,                    -- Location name (e.g., 'lido', 'manasquan')
        buoy_id TEXT,                              -- Buoy ID if applicable
        timestamp DATETIME NOT NULL,               -- Time of reading
        significant_height REAL,                   -- Significant wave height in feet
        primary_swell_height REAL,                 -- Primary swell component height in feet
        primary_swell_period REAL,                 -- Primary swell period in seconds
        primary_swell_direction REAL,              -- Primary swell direction in degrees
        secondary_swell_height REAL,               -- Secondary swell height in feet
        secondary_swell_period REAL,               -- Secondary swell period in seconds
        secondary_swell_direction REAL,            -- Secondary swell direction in degrees
        raw_data TEXT,                             -- JSON representation of full raw data
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP  -- When this record was added
    )
    ''')
    
    # Create indexes for faster querying
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_source_location_time ON swell_readings (source, location, timestamp)')
    
    conn.commit()
    conn.close()
    
    print("Database schema setup complete")

def collect_data_for_specific_times(loc_name, date_obj):
    """
    Collect NDBC buoy data for a specific location at 6am, 12pm, and 6pm.
    
    Args:
        loc_name (str): Location name (e.g., 'lido')
        date_obj (datetime.date): Date to collect data for
        
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
    
    # Determine timezone based on location
    if loc_name.lower() in ['lido', 'rockaways', 'manasquan', 'belmar']:
        local_tz = pytz.timezone('America/New_York')
        print(f"Using Eastern timezone for {loc_name}")
    else:  # West coast locations
        local_tz = pytz.timezone('America/Los_Angeles')
        print(f"Using Pacific timezone for {loc_name}")
    
    # Define target times in local timezone
    target_times = [
        local_tz.localize(datetime.combine(date_obj, datetime.strptime("06:00", "%H:%M").time())),
        local_tz.localize(datetime.combine(date_obj, datetime.strptime("12:00", "%H:%M").time())),
        local_tz.localize(datetime.combine(date_obj, datetime.strptime("18:00", "%H:%M").time()))
    ]
    
    # Convert target times to UTC for API calls
    target_times_utc = [t.astimezone(pytz.UTC) for t in target_times]
    
    processed_data = []
    
    # Collect data for each target time
    for i, target_time in enumerate(target_times_utc):
        local_time = target_times[i]
        print(f"Fetching data for {local_time.strftime('%Y-%m-%d %H:%M')} local time ({target_time.strftime('%Y-%m-%d %H:%M')} UTC)")
        
        # Use find_closest_only=True to get just the closest match
        swell_data = swell.fetch_swell_data(
            swell_buoy_id, 
            target_time, 
            count=500,
            find_closest_only=True
        )
        
        if not swell_data:
            print(f"No swell data found for {loc_name} at {local_time.strftime('%H:%M')}")
            continue
        
        # Convert the single entry to a list if it's not already
        if not isinstance(swell_data, list):
            swell_data = [swell_data]
        
        # Show the data
        print(f"Found {len(swell_data)} data points for {local_time.strftime('%H:%M')}")
        
        # Process the data
        for entry in swell_data:
            # Parse the buoy data structure from swell.py into our database format
            # Extract timestamp - handle both string and datetime formats
            if 'date' in entry:
                if isinstance(entry['date'], str):
                    try:
                        entry_time = datetime.fromisoformat(entry['date'])
                        if entry_time.tzinfo is None:
                            entry_time = entry_time.replace(tzinfo=timezone.utc)
                    except ValueError:
                        print(f"Could not parse date string: {entry['date']}")
                        continue
                else:
                    entry_time = utils.convert_to_utc(entry['date'])
            else:
                print("Entry missing date field, skipping")
                continue
            
            # Process the swell components
            data_point = {
                "timestamp": entry_time,
                "significant_height": entry.get("significant_wave_height")
            }
            
            # Get swell components
            if 'swell_components' in entry:
                components = entry['swell_components']
                
                # Primary swell
                if 'swell_1' in components:
                    primary = components['swell_1']
                    data_point["primary_swell_height"] = primary.get('height')
                    data_point["primary_swell_period"] = primary.get('period')
                    data_point["primary_swell_direction"] = primary.get('direction')
                
                # Secondary swell
                if 'swell_2' in components:
                    secondary = components['swell_2']
                    data_point["secondary_swell_height"] = secondary.get('height')
                    data_point["secondary_swell_period"] = secondary.get('period')
                    data_point["secondary_swell_direction"] = secondary.get('direction')
            
            # Store raw data
            data_point["raw_data"] = json.dumps(entry)
            
            processed_data.append(data_point)
            print(f"Added data point: {entry_time}")
    
    print(f"Processed {len(processed_data)} data points for {loc_name}")
    return processed_data

def save_to_database(location_name, data, buoy_id):
    """Save processed data to the SQLite database."""
    if not data:
        print("No data to save")
        return
    
    conn = sqlite3.connect('swell_data.db')
    cursor = conn.cursor()
    
    # Track saved entries to avoid duplicates
    saved_count = 0
    
    for entry in data:
        # Check if this entry already exists in the database
        timestamp_str = entry["timestamp"].isoformat()
        cursor.execute('''
        SELECT id FROM swell_readings 
        WHERE source = ? AND location = ? AND buoy_id = ? AND timestamp = ?
        ''', ('ndbc_buoy', location_name, buoy_id, timestamp_str))
        
        existing = cursor.fetchone()
        if existing:
            print(f"Entry for {timestamp_str} already exists, skipping")
            continue
        
        # Insert the new entry
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
            timestamp_str,
            entry.get("significant_height"),
            entry.get("primary_swell_height"),
            entry.get("primary_swell_period"),
            entry.get("primary_swell_direction"),
            entry.get("secondary_swell_height"),
            entry.get("secondary_swell_period"),
            entry.get("secondary_swell_direction"),
            entry.get("raw_data")
        ))
        saved_count += 1
    
    conn.commit()
    print(f"Saved {saved_count} new NDBC buoy readings to database")
    conn.close()

def main():
    # Make sure the database exists
    setup_database()
    
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python collect_ndbc_data.py <location> [date]")
        print("Example: python collect_ndbc_data.py lido 2025-05-19")
        return
    
    # Use a different variable name to avoid conflict with the imported module
    loc_name = sys.argv[1]
    
    # Date is optional - defaults to today
    date_obj = None
    if len(sys.argv) >= 3:
        date_str = sys.argv[2]
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD")
            return
    else:
        date_obj = datetime.now().date()
        print(f"No date provided, using today: {date_obj}")
    
    # Get buoy information for location
    buoy_mapping = location.get_buoys_for_location(loc_name)
    if not buoy_mapping:
        print(f"Unknown location: {loc_name}")
        return
    
    buoy_id = buoy_mapping["swell"]
    
    # Collect and process data for specific times
    processed_data = collect_data_for_specific_times(loc_name, date_obj)
    
    # Save to database
    if processed_data:
        save_to_database(loc_name, processed_data, buoy_id)
    else:
        print(f"No data to save for {loc_name}")

if __name__ == "__main__":
    main()
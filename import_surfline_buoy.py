# import_surfline_buoy.py
import sys
import csv
import sqlite3
import json
import os
from datetime import datetime

# Define the absolute path to the shared database
DATABASE_PATH = '/Users/mdietz/surfpy/swell_data.db'
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

def setup_database():
    """Create the database schema if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_PATH)
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
        wind_speed REAL,                           -- Wind speed in knots
        wind_direction REAL,                       -- Wind direction in degrees
        raw_data TEXT,                             -- JSON representation of full raw data
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP  -- When this record was added
    )
    ''')

    # Create indexes for faster querying
    cursor.execute(
        'CREATE INDEX IF NOT EXISTS idx_source_location_time ON swell_readings (source, location, timestamp)')

    conn.commit()
    conn.close()

    print("Database schema setup complete")

def parse_swell_data(swell_str):
    """Parse swell component data from the CSV format."""
    if not swell_str or swell_str.strip() == '':
        return None
    
    try:
        # Check if the format uses pipes
        if '|' in swell_str:
            # Expected format: "Height ft | Period sec | Direction deg"
            parts = swell_str.split('|')
            if len(parts) < 3:
                return None
            
            # Extract height, period, and direction
            height_parts = parts[0].strip().upper().replace('FT', '').strip()
            period_parts = parts[1].strip().upper().replace('SEC', '').strip()
            direction_parts = parts[2].strip().upper().replace('DEG', '').strip()
            
            height = float(height_parts) if height_parts else None
            period = float(period_parts) if period_parts else None
            direction = float(direction_parts) if direction_parts else None
        else:
            # Alternative format without pipes
            # Try to extract values using regular expressions
            import re
            height_match = re.search(r'(\d+\.?\d*)FT', swell_str.upper())
            period_match = re.search(r'(\d+\.?\d*)SEC', swell_str.upper())
            direction_match = re.search(r'(\d+\.?\d*)DEG', swell_str.upper())
            
            height = float(height_match.group(1)) if height_match else None
            period = float(period_match.group(1)) if period_match else None
            direction = float(direction_match.group(1)) if direction_match else None
        
        return {
            "height": height,
            "period": period,
            "direction": direction
        }
    except (ValueError, IndexError) as e:
        print(f"Error parsing swell data: {swell_str} - {str(e)}")
        return None

def import_csv(file_path, location, buoy_id):
    """Import data from a CSV file into the database."""
    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            data = []
            
            for row in reader:
                # Combine date and time to create timestamp
                date_str = row.get('Date', '')
                time_str = row.get('Time', '')
                
                if not date_str or not time_str:
                    print(f"Missing date or time in row: {row}")
                    continue
                
                # Format datetime string
                datetime_str = f"{date_str} {time_str}"
                
                try:
                    # Try to parse the timestamp (adjust format if needed)
                    timestamp = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
                except ValueError:
                    try:
                        # Alternative format with month/day/year
                        timestamp = datetime.strptime(datetime_str, '%m/%d/%Y %H:%M')
                    except ValueError:
                        try:
                            # Format with AM/PM indicator
                            timestamp = datetime.strptime(datetime_str, '%m/%d/%y %I:%M%p')
                        except ValueError:
                            try:
                                # Another possible format with AM/PM
                                timestamp = datetime.strptime(datetime_str, '%m/%d/%Y %I:%M%p')
                            except ValueError:
                                print(f"Invalid timestamp format in row: {datetime_str}")
                                continue
                
                # Parse significant wave height
                significant_height = None
                if 'Significant Height' in row and row['Significant Height']:
                    try:
                        # Handle values like "1FT" or "1.3FT" without spaces
                        height_str = row['Significant Height'].upper()
                        if 'FT' in height_str:
                            # Remove 'FT' and convert to float
                            height_str = height_str.replace('FT', '')
                            significant_height = float(height_str)
                        else:
                            # If there's a space or other format, try the original split approach
                            significant_height = float(row['Significant Height'].split(' ')[0])
                    except (ValueError, IndexError):
                        print(f"Error parsing significant height: {row['Significant Height']}")
                
                # Parse swell components
                swell_components = []
                for i in range(1, 7):  # Up to 6 swells based on your columns
                    swell_key = f'Swell {i}'
                    if swell_key in row and row[swell_key]:
                        swell_data = parse_swell_data(row[swell_key])
                        if swell_data:
                            swell_components.append(swell_data)
                
                # Create data point
                data_point = {
                    "timestamp": timestamp,
                    "significant_height": significant_height
                }
                
                # Add primary swell if available
                if len(swell_components) > 0:
                    data_point["primary_swell_height"] = swell_components[0]["height"]
                    data_point["primary_swell_period"] = swell_components[0]["period"]
                    data_point["primary_swell_direction"] = swell_components[0]["direction"]
                
                # Add secondary swell if available
                if len(swell_components) > 1:
                    data_point["secondary_swell_height"] = swell_components[1]["height"]
                    data_point["secondary_swell_period"] = swell_components[1]["period"]
                    data_point["secondary_swell_direction"] = swell_components[1]["direction"]
                
                # Store raw data as JSON
                data_point["raw_data"] = json.dumps({
                    "significant_height": data_point.get("significant_height"),
                    "swell_components": swell_components,
                    "peak_period": row.get("Peak Period", ""),
                    "mean_direction": row.get("Mean Direction", ""),
                    "wave_energy": row.get("Wave Energy", "")
                })
                
                data.append(data_point)
            
            # Save to database
            if data:
                save_to_database(location, data, buoy_id)
            else:
                print("No valid data found in the CSV file")
            
    except Exception as e:
        print(f"Error importing CSV: {str(e)}")
        import traceback
        traceback.print_exc()

def save_to_database(location, data, buoy_id):
    """Save processed data to the SQLite database."""
    if not data:
        print("No data to save")
        return
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    saved_count = 0
    skipped_count = 0
    
    for entry in data:
        # Check if entry already exists
        cursor.execute('''
        SELECT id FROM swell_readings 
        WHERE source = ? AND location = ? AND buoy_id = ? AND timestamp = ?
        ''', ('surfline_buoy', location, buoy_id, entry["timestamp"].isoformat()))
        
        existing = cursor.fetchone()
        if existing:
            print(f"Entry for {entry['timestamp']} already exists in database, skipping")
            skipped_count += 1
            continue
        
        cursor.execute('''
        INSERT INTO swell_readings (
            source, location, buoy_id, timestamp, 
            significant_height, primary_swell_height, primary_swell_period, primary_swell_direction,
            secondary_swell_height, secondary_swell_period, secondary_swell_direction,
            wind_speed, wind_direction, raw_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'surfline_buoy', 
            location, 
            buoy_id, 
            entry["timestamp"].isoformat(),
            entry.get("significant_height"),
            entry.get("primary_swell_height"),
            entry.get("primary_swell_period"),
            entry.get("primary_swell_direction"),
            entry.get("secondary_swell_height"),
            entry.get("secondary_swell_period"),
            entry.get("secondary_swell_direction"),
            entry.get("wind_speed"),
            entry.get("wind_direction"),
            entry.get("raw_data")
        ))
        saved_count += 1
    
    conn.commit()
    print(f"Saved {saved_count} new Surfline buoy readings to database")
    print(f"Skipped {skipped_count} existing entries")
    conn.close()

def main():
    # Setup database
    setup_database()
    
    # Check command line arguments
    if len(sys.argv) < 4:
        print("Usage: python import_surfline_buoy.py <csv_file> <location> <buoy_id>")
        print("Example: python import_surfline_buoy.py surfline_buoy_data.csv lido 44065")
        return
    
    csv_file = sys.argv[1]
    location = sys.argv[2].lower()
    buoy_id = sys.argv[3]
    
    import_csv(csv_file, location, buoy_id)

if __name__ == "__main__":
    main()
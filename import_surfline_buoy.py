# import_surfline_buoy.py
import sys
import csv
import sqlite3
import json
from datetime import datetime

def parse_swell_components(row):
    """Parse swell components from a row of data."""
    components = []
    
    # Check for multiple swell components
    for i in range(1, 6):  # Up to 5 components
        height_key = f"swell_{i}_height"
        period_key = f"swell_{i}_period"
        direction_key = f"swell_{i}_direction"
        
        if height_key in row and row[height_key]:
            try:
                height = float(row[height_key])
                if height > 0:
                    component = {
                        "height": height,
                        "period": float(row[period_key]) if row.get(period_key) else None,
                        "direction": float(row[direction_key]) if row.get(direction_key) else None
                    }
                    components.append(component)
            except (ValueError, TypeError):
                pass
    
    return components

def import_csv(file_path, location, buoy_id):
    """Import data from a CSV file into the database."""
    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            data = []
            
            for row in reader:
                # Parse timestamp
                try:
                    timestamp = datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M')
                except ValueError:
                    print(f"Invalid timestamp format in row: {row}")
                    continue
                
                # Parse swell components
                swell_components = parse_swell_components(row)
                
                # Create data point
                data_point = {
                    "timestamp": timestamp,
                    "significant_height": float(row['significant_height']) if row.get('significant_height') else None
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
                
                # Add wind data if available
                if 'wind_speed' in row and row['wind_speed']:
                    data_point["wind_speed"] = float(row['wind_speed'])
                if 'wind_direction' in row and row['wind_direction']:
                    data_point["wind_direction"] = float(row['wind_direction'])
                
                # Store raw data as JSON
                data_point["raw_data"] = json.dumps({
                    "significant_height": data_point.get("significant_height"),
                    "swell_components": swell_components,
                    "wind_speed": data_point.get("wind_speed"),
                    "wind_direction": data_point.get("wind_direction")
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
    
    conn = sqlite3.connect('swell_data.db')
    cursor = conn.cursor()
    
    for entry in data:
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
    
    conn.commit()
    print(f"Saved {len(data)} Surfline buoy readings to database")
    conn.close()

def main():
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
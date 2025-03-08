#!/usr/bin/env python3
import json
import subprocess
import sqlite3
from datetime import datetime
import os
import sys
import time
import argparse

def setup_database():
    """Create/connect to the database and set up tables if they don't exist."""
    conn = sqlite3.connect('surf_data.db')
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS spots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        latitude REAL,
        longitude REAL,
        country TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS swell_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        spot_id INTEGER,
        buoy_id TEXT,
        buoy_lat REAL,
        buoy_lng REAL,
        fetch_date TIMESTAMP,
        data TEXT,
        FOREIGN KEY (spot_id) REFERENCES spots(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS met_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        spot_id INTEGER,
        buoy_id TEXT,
        buoy_lat REAL,
        buoy_lng REAL,
        fetch_date TIMESTAMP,
        data TEXT,
        FOREIGN KEY (spot_id) REFERENCES spots(id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tide_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        spot_id INTEGER,
        station_id TEXT,
        station_lat REAL,
        station_lng REAL,
        fetch_date TIMESTAMP,
        data TEXT,
        FOREIGN KEY (spot_id) REFERENCES spots(id)
    )
    ''')
    
    conn.commit()
    return conn, cursor

def load_spots(json_file):
    """Load surf spots from the JSON file."""
    with open(json_file, 'r') as f:
        return json.load(f)

def save_spot_to_db(cursor, spot):
    """Save a spot to the database if it doesn't exist already."""
    cursor.execute(
        "INSERT OR IGNORE INTO spots (name, latitude, longitude, country) VALUES (?, ?, ?, ?)",
        (spot['name'], float(spot['lat']), float(spot['lng']), spot['country'])
    )
    
    # Get spot_id (either newly created or existing)
    cursor.execute("SELECT id FROM spots WHERE name = ?", (spot['name'],))
    return cursor.fetchone()[0]

def run_data_collection(spot_id, lat, lng):
    """Run the data collection scripts for a spot and return the results."""
    results = {
        'swell': None,
        'met': None,
        'tide': None
    }
    
def run_data_collection(spot_id, lat, lng):
    """Run the data collection scripts for a spot and return the results."""
    results = {
        'swell': None,
        'met': None,
        'tide': None
    }
    
    # Run get_swell.py
    try:
        print(f"Fetching swell data for {lat}, {lng}...")
        output = subprocess.check_output(['python', 'get_swell.py', str(lat), str(lng)], 
                                         stderr=subprocess.STDOUT, text=True)
        
        # Extract JSON from the output
        json_str = extract_json_from_output(output)
        if json_str:
            results['swell'] = json.loads(json_str)
            print(f"Successfully extracted swell data")
        else:
            print(f"Warning: Could not extract valid JSON from swell output")
            print(f"Output was: {output}")
    except subprocess.CalledProcessError as e:
        print(f"Error getting swell data: {e.output}")
    except json.JSONDecodeError as e:
        print(f"Error parsing swell data JSON: {e}")
    except Exception as e:
        print(f"Unexpected error processing swell data: {str(e)}")
    
    # Run get_met.py
    try:
        print(f"Fetching meteorological data for {lat}, {lng}...")
        output = subprocess.check_output(['python', 'get_met.py', str(lat), str(lng)], 
                                         stderr=subprocess.STDOUT, text=True)
        
        # Extract JSON from the output
        json_str = extract_json_from_output(output)
        if json_str:
            results['met'] = json.loads(json_str)
        else:
            print(f"Warning: Could not extract valid JSON from meteorological output")
            print(f"Output was: {output}")
    except subprocess.CalledProcessError as e:
        print(f"Error getting meteorological data: {e.output}")
    except json.JSONDecodeError as e:
        print(f"Error parsing meteorological data JSON: {e}")
        print(f"Output was: {output}")
    
    # Run get_tide.py
    try:
        print(f"Fetching tide data for {lat}, {lng}...")
        output = subprocess.check_output(['python', 'get_tide.py', str(lat), str(lng)], 
                                         stderr=subprocess.STDOUT, text=True)
        
        # Extract JSON from the output
        json_str = extract_json_from_output(output)
        if json_str:
            results['tide'] = json.loads(json_str)
        else:
            print(f"Warning: Could not extract valid JSON from tide output")
            print(f"Output was: {output}")
    except subprocess.CalledProcessError as e:
        print(f"Error getting tide data: {e.output}")
    except json.JSONDecodeError as e:
        print(f"Error parsing tide data JSON: {e}")
        print(f"Output was: {output}")
    
    return results

def extract_json_from_output(output):
    """Extract JSON from command output more robustly."""
    # First try a more comprehensive approach to find JSON blocks
    lines = output.strip().split('\n')
    
    # Look for the last complete JSON object
    for i in range(len(lines) - 1, -1, -1):  # Start from the end
        line = lines[i].strip()
        if line.startswith('{') and line.endswith('}'):
            try:
                result = json.loads(line)
                return line  # Found valid JSON
            except json.JSONDecodeError:
                pass
            
    # If that didn't work, try to find a multi-line JSON object
    # This looks for an opening brace and collects lines until a closing brace
    in_json = False
    json_lines = []
    open_braces = 0
    
    for line in lines:
        if not in_json and '{' in line:
            in_json = True
            
        if in_json:
            json_lines.append(line)
            open_braces += line.count('{') - line.count('}')
            
            if open_braces == 0:
                # We have a complete JSON object
                json_str = ''.join(json_lines)
                try:
                    # Check if it's valid JSON
                    json.loads(json_str)
                    return json_str
                except json.JSONDecodeError:
                    # Reset and keep looking
                    in_json = False
                    json_lines = []
    
    # If all else fails, try a regex approach to find any JSON-like structure
    import re
    json_pattern = r'(\{[^{}]*(\{[^{}]*\})*[^{}]*\})'
    matches = re.findall(json_pattern, output)
    
    if matches:
        for match in reversed(matches):  # Try from the last match (likely the result)
            try:
                json.loads(match[0])
                return match[0]
            except json.JSONDecodeError:
                continue
    
    # Last resort: check if the whole output is valid JSON
    try:
        json.loads(output)
        return output
    except json.JSONDecodeError:
        pass
    
    return None  # No valid JSON found

def save_data_to_db(conn, cursor, spot_id, data):
    """Save the collected data to the database."""
    now = datetime.now()
    
    # Save swell data if available
    if data['swell']:
        try:
            # Check if we have buoy_info
            buoy_id = None
            buoy_lat = None
            buoy_lng = None
            
            if 'buoy_info' in data['swell']:
                buoy_info = data['swell']['buoy_info']
                buoy_id = buoy_info.get('id')
                if 'location' in buoy_info:
                    buoy_lat = buoy_info['location'].get('latitude')
                    buoy_lng = buoy_info['location'].get('longitude')
            
            # Insert the data
            cursor.execute(
                "INSERT INTO swell_data (spot_id, buoy_id, buoy_lat, buoy_lng, fetch_date, data) VALUES (?, ?, ?, ?, ?, ?)",
                (spot_id, buoy_id, buoy_lat, buoy_lng, now, json.dumps(data['swell']))
            )
            print(f"Saved swell data to database for spot_id {spot_id}")
        except Exception as e:
            print(f"Error saving swell data: {e}")
            print(f"Data: {data['swell']}")
    
    # Save meteorological data if available
    if data['met']:
        try:
            # Check if we have buoy_info
            buoy_id = None
            buoy_lat = None
            buoy_lng = None
            
            if 'buoy_info' in data['met']:
                buoy_info = data['met']['buoy_info']
                buoy_id = buoy_info.get('id')
                if 'location' in buoy_info:
                    buoy_lat = buoy_info['location'].get('latitude')
                    buoy_lng = buoy_info['location'].get('longitude')
            
            # Insert the data
            cursor.execute(
                "INSERT INTO met_data (spot_id, buoy_id, buoy_lat, buoy_lng, fetch_date, data) VALUES (?, ?, ?, ?, ?, ?)",
                (spot_id, buoy_id, buoy_lat, buoy_lng, now, json.dumps(data['met']))
            )
            print(f"Saved meteorological data to database for spot_id {spot_id}")
        except Exception as e:
            print(f"Error saving meteorological data: {e}")
            print(f"Data: {data['met']}")
    
    # Save tide data if available
    if data['tide']:
        try:
            # Check if we have station info
            station_id = data['tide'].get('station_id')
            station_lat = None
            station_lng = None
            
            if 'location' in data['tide']:
                station_lat = data['tide']['location'].get('latitude')
                station_lng = data['tide']['location'].get('longitude')
            
            # Insert the data
            cursor.execute(
                "INSERT INTO tide_data (spot_id, station_id, station_lat, station_lng, fetch_date, data) VALUES (?, ?, ?, ?, ?, ?)",
                (spot_id, station_id, station_lat, station_lng, now, json.dumps(data['tide']))
            )
            print(f"Saved tide data to database for spot_id {spot_id}")
        except Exception as e:
            print(f"Error saving tide data: {e}")
            print(f"Data: {data['tide']}")
    
    conn.commit()

def main():
    parser = argparse.ArgumentParser(description='Collect surf data for spots in a JSON file.')
    parser.add_argument('--file', default='surfspots.json', help='JSON file containing surf spots')
    parser.add_argument('--limit', type=int, help='Limit the number of spots to process')
    parser.add_argument('--delay', type=int, default=1, help='Delay between API calls in seconds')
    args = parser.parse_args()
    
    conn, cursor = setup_database()
    spots = load_spots(args.file)
    
    if args.limit:
        spots = spots[:args.limit]
    
    total_spots = len(spots)
    spots_with_swell = 0
    spots_with_met = 0
    spots_with_tide = 0
    
    print(f"Starting data collection for {total_spots} spots...")
    
    for i, spot in enumerate(spots, 1):
        print(f"Processing spot {i}/{total_spots}: {spot['name']}, {spot['country']}")
        
        # Save spot to database and get its ID
        spot_id = save_spot_to_db(cursor, spot)
        
        # Collect data
        data = run_data_collection(spot_id, spot['lat'], spot['lng'])
        
        # Check if the data is a proper structure before counting it
        if data['swell'] and isinstance(data['swell'], dict) and ('wave_data' in data['swell'] or 'buoy_info' in data['swell']):
            spots_with_swell += 1
            print(f"Valid swell data found")
        
        if data['met'] and isinstance(data['met'], dict) and ('meteorological_data' in data['met'] or 'buoy_info' in data['met']):
            spots_with_met += 1
            print(f"Valid meteorological data found")
        
        if data['tide'] and isinstance(data['tide'], dict) and ('water_level' in data['tide'] or 'station_id' in data['tide']):
            spots_with_tide += 1
            print(f"Valid tide data found")
        
        # Save data to database
        save_data_to_db(conn, cursor, spot_id, data)
        
        # ... rest of the code ...
        
        print(f"Completed {spot['name']} ({i}/{total_spots})")
        
        # Add delay to avoid overwhelming APIs
        if i < total_spots and args.delay > 0:
            time.sleep(args.delay)
    
    # Print summary
    print("\n=== COLLECTION SUMMARY ===")
    print(f"Total spots processed: {total_spots}")
    print(f"Spots with swell data: {spots_with_swell} ({spots_with_swell/total_spots*100:.1f}%)")
    print(f"Spots with meteorological data: {spots_with_met} ({spots_with_met/total_spots*100:.1f}%)")
    print(f"Spots with tide data: {spots_with_tide} ({spots_with_tide/total_spots*100:.1f}%)")
    
    conn.close()

if __name__ == "__main__":
    main()
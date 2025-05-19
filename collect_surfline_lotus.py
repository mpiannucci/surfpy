# collect_surfline_lotus.py
import sys
import sqlite3
import json
from datetime import datetime, date
import pysurfline
import pandas as pd

# Spot IDs mapping 
SPOT_IDS = {
    "rockaways": "5842041f4e65fad6a7708852",
    "lido": "5842041f4e65fad6a77089e2",
    "belmar": "5842041f4e65fad6a7708a01",
    "manasquan": "5842041f4e65fad6a7708856"
}

def get_surf_data(spot_id, date_obj):
    """
    Get Surfline forecast data for a specific spot and date
    
    Args:
        spot_id (str): Surfline spot ID
        date_obj (date): Date to fetch data for
        
    Returns:
        list: List of hourly data points for the day
    """
    # Calculate how many days from today
    today = datetime.now().date()
    days_from_today = (date_obj - today).days
    
    # If requesting future dates, limit to forecast horizon
    if days_from_today < 0:
        print("Warning: Requesting data for past date. Limited historical data may be available.")
        days = 1  # Just today's data
    elif days_from_today > 6:
        print("Warning: Requesting data too far in future. Limiting to 6-day forecast.")
        days = 6
    else:
        days = days_from_today + 1  # Include today
    
    try:
        # Get forecasts
        spot_forecasts = pysurfline.get_spot_forecasts(
            spot_id,
            days=days,
            intervalHours=1,
        )
        
        # Get forecast dataframe
        forecast_df = spot_forecasts.get_dataframe()
        
        # Filter to only include the requested date
        if forecast_df.empty:
            print(f"No data found for spot ID {spot_id}")
            return []
        
        # Convert the timestamp column to datetime if it's not already
        if not isinstance(forecast_df['timestamp_dt'].iloc[0], datetime):
            forecast_df['timestamp_dt'] = pd.to_datetime(forecast_df['timestamp_dt'])
        
        # Filter to the requested date
        filtered_df = forecast_df[forecast_df['timestamp_dt'].dt.date == date_obj]
        
        if filtered_df.empty:
            print(f"No data found for date {date_obj}")
            return []
        
        # Convert to list of dictionaries
        hourly_data = []
        for _, row in filtered_df.iterrows():
            data_point = {
                "timestamp": row['timestamp_dt'],
                "significant_height": None  # Surfline doesn't provide this directly
            }
            
            # Add primary swell if available
            if 'swells_0_height' in row and row['swells_0_height'] > 0:
                data_point["primary_swell_height"] = row['swells_0_height']
                data_point["primary_swell_period"] = row['swells_0_period']
                data_point["primary_swell_direction"] = row['swells_0_direction']
            
            # Add secondary swell if available
            if 'swells_1_height' in row and row['swells_1_height'] > 0:
                data_point["secondary_swell_height"] = row['swells_1_height']
                data_point["secondary_swell_period"] = row['swells_1_period']
                data_point["secondary_swell_direction"] = row['swells_1_direction']
            
            # Add wind data if available
            if 'speed' in row:
                data_point["wind_speed"] = row['speed']
            if 'direction' in row:
                data_point["wind_direction"] = row['direction']
            
            # Store raw data as JSON
            data_point["raw_data"] = json.dumps({
                key: value for key, value in row.items() 
                if key.startswith('swells_') or key in ['speed', 'direction', 'surf_optimalScore', 'temperature']
            })
            
            hourly_data.append(data_point)
        
        return hourly_data
        
    except Exception as e:
        print(f"Error getting Surfline data: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def save_to_database(location, data, spot_id):
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
            'surfline_lotus', 
            location, 
            spot_id, 
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
    print(f"Saved {len(data)} Surfline LOTUS readings to database")
    conn.close()

def main():
    # Check command line arguments
    if len(sys.argv) < 3:
        print("Usage: python collect_surfline_lotus.py <location> <date>")
        print("Example: python collect_surfline_lotus.py lido 2025-05-19")
        return
    
    location = sys.argv[1].lower()
    date_str = sys.argv[2]
    
    # Check if location is valid
    if location not in SPOT_IDS:
        print(f"Invalid location. Available locations: {', '.join(SPOT_IDS.keys())}")
        return
    
    # Parse date
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD")
        return
    
    spot_id = SPOT_IDS[location]
    
    # Get data
    data = get_surf_data(spot_id, date_obj)
    
    # Save to database
    save_to_database(location, data, spot_id)

if __name__ == "__main__":
    main()
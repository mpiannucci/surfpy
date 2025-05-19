# db_schema.py
import sqlite3

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
        wind_speed REAL,                           -- Wind speed in knots
        wind_direction REAL,                       -- Wind direction in degrees
        raw_data TEXT,                             -- JSON representation of full raw data
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP  -- When this record was added
    )
    ''')
    
    # Create indexes for faster querying
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_source_location_time ON swell_readings (source, location, timestamp)')
    
    conn.commit()
    conn.close()
    
    print("Database schema setup complete")

if __name__ == "__main__":
    setup_database()
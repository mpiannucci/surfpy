#!/usr/bin/env python3
import sqlite3
import json
from datetime import datetime
import argparse

def connect_db():
    """Connect to the database."""
    conn = sqlite3.connect('surf_data.db')
    conn.row_factory = sqlite3.Row  # This enables column access by name
    cursor = conn.cursor()
    return conn, cursor

def list_spots(cursor, country=None):
    """List all spots in the database, optionally filtered by country."""
    if country:
        cursor.execute("""
            SELECT s.id, s.name, s.country, s.latitude, s.longitude,
                   COUNT(DISTINCT sw.id) as swell_count,
                   COUNT(DISTINCT m.id) as met_count,
                   COUNT(DISTINCT t.id) as tide_count
            FROM spots s
            LEFT JOIN swell_data sw ON s.id = sw.spot_id
            LEFT JOIN met_data m ON s.id = m.spot_id
            LEFT JOIN tide_data t ON s.id = t.spot_id
            WHERE s.country LIKE ?
            GROUP BY s.id
            ORDER BY s.name
        """, (f"%{country}%",))
    else:
        cursor.execute("""
            SELECT s.id, s.name, s.country, s.latitude, s.longitude,
                   COUNT(DISTINCT sw.id) as swell_count,
                   COUNT(DISTINCT m.id) as met_count,
                   COUNT(DISTINCT t.id) as tide_count
            FROM spots s
            LEFT JOIN swell_data sw ON s.id = sw.spot_id
            LEFT JOIN met_data m ON s.id = m.spot_id
            LEFT JOIN tide_data t ON s.id = t.spot_id
            GROUP BY s.id
            ORDER BY s.name
        """)
    
    return cursor.fetchall()

def show_spot_data(cursor, spot_id):
    """Show detailed data for a specific spot."""
    # Get spot info
    cursor.execute("SELECT * FROM spots WHERE id = ?", (spot_id,))
    spot = cursor.fetchone()
    
    if not spot:
        return None, None, None, None
    
    # Get latest swell data
    cursor.execute("""
        SELECT * FROM swell_data 
        WHERE spot_id = ? 
        ORDER BY fetch_date DESC 
        LIMIT 1
    """, (spot_id,))
    swell = cursor.fetchone()
    
    # Get latest meteorological data
    cursor.execute("""
        SELECT * FROM met_data 
        WHERE spot_id = ? 
        ORDER BY fetch_date DESC 
        LIMIT 1
    """, (spot_id,))
    met = cursor.fetchone()
    
    # Get latest tide data
    cursor.execute("""
        SELECT * FROM tide_data 
        WHERE spot_id = ? 
        ORDER BY fetch_date DESC 
        LIMIT 1
    """, (spot_id,))
    tide = cursor.fetchone()
    
    return spot, swell, met, tide

def get_summary_stats(cursor):
    """Get summary statistics from the database."""
    # Total number of spots
    cursor.execute("SELECT COUNT(*) FROM spots")
    total_spots = cursor.fetchone()[0]
    
    # Spots with data
    cursor.execute("SELECT COUNT(DISTINCT spot_id) FROM swell_data")
    spots_with_swell = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT spot_id) FROM met_data")
    spots_with_met = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT spot_id) FROM tide_data")
    spots_with_tide = cursor.fetchone()[0]
    
    # Spots with all three data types
    cursor.execute("""
        SELECT COUNT(*) FROM (
            SELECT spot_id
            FROM swell_data
            GROUP BY spot_id
            INTERSECT
            SELECT spot_id
            FROM met_data
            GROUP BY spot_id
            INTERSECT
            SELECT spot_id
            FROM tide_data
            GROUP BY spot_id
        )
    """)
    spots_with_all = cursor.fetchone()[0]
    
    # Countries represented
    cursor.execute("SELECT COUNT(DISTINCT country) FROM spots")
    country_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT country, COUNT(*) as spot_count FROM spots GROUP BY country ORDER BY spot_count DESC LIMIT 10")
    top_countries = cursor.fetchall()
    
    return {
        'total_spots': total_spots,
        'spots_with_swell': spots_with_swell,
        'spots_with_met': spots_with_met,
        'spots_with_tide': spots_with_tide,
        'spots_with_all': spots_with_all,
        'country_count': country_count,
        'top_countries': top_countries
    }

def print_spot_data(spot, swell, met, tide):
    """Pretty print the data for a spot."""
    print(f"\n=== {spot['name']}, {spot['country']} ===")
    print(f"Location: {spot['latitude']}, {spot['longitude']}")
    
    # Print swell data
    if swell:
        swell_data = json.loads(swell['data'])
        print("\n--- SWELL DATA ---")
        print(f"Buoy: {swell['buoy_id']} at {swell['buoy_lat']}, {swell['buoy_lng']}")
        print(f"Fetched: {swell['fetch_date']}")
        
        if 'wave_data' in swell_data and swell_data['wave_data']:
            wave = swell_data['wave_data'][0]
            print(f"Date: {wave.get('date', 'N/A')}")
            
            if 'swell_components' in wave:
                for comp, data in wave['swell_components'].items():
                    print(f"  {comp}: H={data.get('height', 'N/A')}m, P={data.get('period', 'N/A')}s, Dir={data.get('direction', 'N/A')}°")
            else:
                for key, value in wave.items():
                    if key != 'date':
                        print(f"  {key}: {value}")
    else:
        print("\nNo swell data available")
    
    # Print meteorological data
    if met:
        met_data = json.loads(met['data'])
        print("\n--- METEOROLOGICAL DATA ---")
        print(f"Buoy: {met['buoy_id']} at {met['buoy_lat']}, {met['buoy_lng']}")
        print(f"Fetched: {met['fetch_date']}")
        
        if 'meteorological_data' in met_data and met_data['meteorological_data']:
            m = met_data['meteorological_data'][0]
            print(f"Date: {m.get('date', 'N/A')}")
            for key, value in m.items():
                if key != 'date':
                    print(f"  {key}: {value}")
    else:
        print("\nNo meteorological data available")
    
    # Print tide data
    if tide:
        tide_data = json.loads(tide['data'])
        print("\n--- TIDE DATA ---")
        print(f"Station: {tide['station_id']} at {tide['station_lat']}, {tide['station_lng']}")
        print(f"Fetched: {tide['fetch_date']}")
        print(f"Date: {tide_data.get('date', 'N/A')}")
        print(f"Water Level: {tide_data.get('water_level', 'N/A')} {tide_data.get('units', '')}")
    else:
        print("\nNo tide data available")

def main():
    parser = argparse.ArgumentParser(description='View surf data from the database.')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # List spots command
    list_parser = subparsers.add_parser('list', help='List spots in the database')
    list_parser.add_argument('--country', help='Filter spots by country')
    
    # View spot command
    view_parser = subparsers.add_parser('view', help='View data for a specific spot')
    view_parser.add_argument('spot_id', type=int, help='ID of the spot to view')
    
    # Summary command
    subparsers.add_parser('summary', help='Show summary statistics')
    
    args = parser.parse_args()
    
    conn, cursor = connect_db()
    
    if args.command == 'list':
        spots = list_spots(cursor, args.country)
        
        print(f"Found {len(spots)} spots")
        print("\nID | Name | Country | Data Available (Swell/Met/Tide)")
        print("-" * 70)
        
        for spot in spots:
            data_status = f"{spot['swell_count']}/{spot['met_count']}/{spot['tide_count']}"
            print(f"{spot['id']} | {spot['name']} | {spot['country']} | {data_status}")
    
    elif args.command == 'view':
        spot, swell, met, tide = show_spot_data(cursor, args.spot_id)
        
        if spot:
            print_spot_data(spot, swell, met, tide)
        else:
            print(f"No spot found with ID {args.spot_id}")
    
    elif args.command == 'summary':
        stats = get_summary_stats(cursor)
        
        print("\n=== DATABASE SUMMARY ===")
        print(f"Total spots: {stats['total_spots']}")
        print(f"Spots with swell data: {stats['spots_with_swell']} ({stats['spots_with_swell']/stats['total_spots']*100:.1f}%)")
        print(f"Spots with meteorological data: {stats['spots_with_met']} ({stats['spots_with_met']/stats['total_spots']*100:.1f}%)")
        print(f"Spots with tide data: {stats['spots_with_tide']} ({stats['spots_with_tide']/stats['total_spots']*100:.1f}%)")
        print(f"Spots with all three data types: {stats['spots_with_all']} ({stats['spots_with_all']/stats['total_spots']*100:.1f}%)")
        print(f"Countries represented: {stats['country_count']}")
        
        print("\nTop countries by number of spots:")
        for country in stats['top_countries']:
            print(f"  {country['country']}: {country['spot_count']} spots")
    
    else:
        parser.print_help()
    
    conn.close()

if __name__ == "__main__":
    main()
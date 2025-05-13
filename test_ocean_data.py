# test_ocean_data.py
from datetime import datetime
import pytz
from ocean_data import swell, meteorology, tide, location

def main():
    """Test the ocean_data package modules."""
    # Set up test parameters
    test_location = "lido"
    eastern = pytz.timezone('America/New_York')
    test_time = eastern.localize(datetime(2025, 5, 13, 10, 0))
    
    # Get buoy IDs for location
    buoy_info = location.get_buoys_for_location(test_location)
    if not buoy_info:
        print(f"Error: Location '{test_location}' not found")
        return
        
    print(f"Testing ocean_data package for {test_location} at {test_time}")
    print("-" * 60)
    
    # Test swell data
    print("\nFetching swell data...")
    swell_data = swell.fetch_swell_data(buoy_info["swell"], test_time)
    print(f"Swell data: {swell_data}")
    
    # Test meteorological data
    print("\nFetching meteorological data...")
    met_data = meteorology.fetch_meteorological_data(buoy_info["met"], test_time)
    print(f"Meteorological data: {met_data}")
    
    # Test tide data
    print("\nFetching tide data...")
    tide_data = tide.fetch_water_level(buoy_info["tide"], test_time)
    print(f"Tide data: {tide_data}")
    
if __name__ == "__main__":
    main()
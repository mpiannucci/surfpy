"""
Ocean Data Module - Location

This module provides functions for mapping surf locations to 
oceanographic data sources and handling location-based operations.

Functions:
    - get_buoys_for_location: Get buoy IDs for a specific surf spot
    - get_all_locations: Get a list of all supported locations
    - is_valid_location: Check if a location is supported
"""

# Location to buoy/station mapping
LOCATION_TO_BUOYS = {
    "lido": {"swell": "44065", "met": "44009", "tide": "8516402"},
    "manasquan": {"swell": "44091", "met": "44009", "tide": "8533051"},
    "rockaways": {"swell": "44065", "met": "44009", "tide": "8516881"},
    "belmar": {"swell": "44091", "met": "44009", "tide": "8533051"},
    "steamer_lane": {"swell": "46042", "met": "46042", "tide": "9413450"},
    "trestles": {"swell": "46277", "met": "46277", "tide": "9410230"}
}

def get_buoys_for_location(location):
    """
    Get buoy IDs for a specific surf spot.
    
    Args:
        location (str): Location name (case insensitive)
        
    Returns:
        dict: Mapping of data types to buoy/station IDs or None if location not found
    """
    location_lower = location.lower() if location else ""
    return LOCATION_TO_BUOYS.get(location_lower)

def get_all_locations():
    """
    Get a list of all supported locations.
    
    Returns:
        list: List of supported location names
    """
    return list(LOCATION_TO_BUOYS.keys())

def is_valid_location(location):
    """
    Check if a location is supported.
    
    Args:
        location (str): Location name to check
        
    Returns:
        bool: True if location is supported, False otherwise
    """
    location_lower = location.lower() if location else ""
    return location_lower in LOCATION_TO_BUOYS

def get_location_info(location):
    """
    Get detailed information about a location.
    
    Args:
        location (str): Location name
        
    Returns:
        dict: Location information including name, buoys, and coordinates (if available)
    """
    location_lower = location.lower() if location else ""
    
    # Location coordinates (latitude, longitude)
    # You could expand this with more detailed information
    location_coords = {
        "lido": {"lat": 40.5898, "lon": -73.5768},
        "manasquan": {"lat": 40.1023, "lon": -74.0334},
        "rockaways": {"lat": 40.5832, "lon": -73.8157},
        "belmar": {"lat": 40.1762, "lon": -74.0121}
    }
    
    buoys = LOCATION_TO_BUOYS.get(location_lower)
    
    if not buoys:
        return None
        
    return {
        "name": location,
        "buoys": buoys,
        "coordinates": location_coords.get(location_lower)
    }
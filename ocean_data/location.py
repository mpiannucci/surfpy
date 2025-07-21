"""
Ocean Data Module - Location

This module provides functions for mapping surf locations to 
oceanographic data sources and handling location-based operations.
"""

import surfpy
from surfpy.location import Location
import database_utils

# Mapping from old location names to new slugs for backward compatibility
LEGACY_LOCATION_MAP = {
    "lido": "lido-beach",
    "manasquan": "manasquan-beach",
    "rockaways": "rockaways-beach",
    "belmar": "belmar-beach",
    "steamer_lane": "steamer-lane",
    "trestles": "trestles-beach"
}

def get_spot_config(spot_name):
    """
    Get the full configuration for a specific surf spot from the database.
    
    Args:
        spot_name (str): The slug/name of the surf spot.
        
    Returns:
        dict: The configuration dictionary for the spot, or None if not found.
    """
    # Try to find by slug first
    spot = database_utils.get_surf_spot_by_slug(spot_name)
    if not spot:
        # If not found by slug, try to find by name
        spot = database_utils.get_surf_spot_by_name(spot_name)

    if spot:
        # Convert database record to the expected format
        return {
            "name": spot["name"],
            "swell_buoy_id": spot["swell_buoy_id"],
            "tide_station_id": spot["tide_station_id"],
            "wind_location": {"lat": spot["wind_lat"], "lon": spot["wind_long"]},
            "breaking_wave_params": {
                "depth": spot["breaking_wave_depth"],
                "angle": spot["breaking_wave_angle"],
                "slope": spot["breaking_wave_slope"]
            },
            "timezone": spot["timezone"],
            "met_buoy_id": spot["met_buoy_id"]
        }
    return None

def get_all_locations():
    """
    Get a list of all supported location slugs from the database.
    
    Returns:
        list: List of supported location slugs.
    """
    spots = database_utils.get_all_surf_spots()
    return [spot['slug'] for spot in spots]

def is_valid_location(location):
    """
    Check if a location is supported, handling both new slugs and legacy names.
    
    Args:
        location (str): Location name or slug to check.
        
    Returns:
        bool: True if location is supported, False otherwise.
    """
    location_lower = location.lower() if location else ""
    
    # First, check if it's a direct slug or name in the database using the enhanced get_spot_config
    spot = get_spot_config(location_lower)
    if spot:
        return True
        
    # If not, check if it's a legacy name that can be mapped to a slug in the database
    spot_slug = LEGACY_LOCATION_MAP.get(location_lower)
    if spot_slug:
        spot = get_spot_config(spot_slug) # Use get_spot_config to check the mapped slug
        if spot:
            return True
            
    return False

def get_buoys_for_location(location):
    """
    Get buoy IDs for a specific surf spot for backward compatibility with older endpoints.
    
    Args:
        location (str): Location name (case insensitive).
        
    Returns:
        dict: Mapping of data types to buoy/station IDs or None if location not found.
    """
    location_lower = location.lower() if location else ""
    
    # Map legacy name to new slug if necessary
    spot_slug = LEGACY_LOCATION_MAP.get(location_lower, location_lower)
    
    config = get_spot_config(spot_slug)
    if not config:
        return None
        
    # Return the structure expected by the old surf session endpoints
    return {
        "swell": config["swell_buoy_id"],
        "met": config.get("met_buoy_id", config["swell_buoy_id"]),
        "tide": config["tide_station_id"]
    }

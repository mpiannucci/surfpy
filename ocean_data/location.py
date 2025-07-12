"""
Ocean Data Module - Location

This module provides functions for mapping surf locations to 
oceanographic data sources and handling location-based operations.
"""

# Comprehensive configuration for each surf spot
SURF_SPOTS_CONFIG = {
    "lido-beach": {
        "name": "Lido Beach, NY",
        "swell_buoy_id": "44065",
        "tide_station_id": "8516663",
        "wind_location": {"lat": 40.58, "lon": -73.66},
        "breaking_wave_params": {
            "depth": 5.0,
            "angle": 160.0,
            "slope": 0.02
        }
    },
    "manasquan-beach": {
        "name": "Manasquan Beach, NJ",
        "swell_buoy_id": "44091",
        "tide_station_id": "8532337",
        "wind_location": {"lat": 40.11, "lon": -74.03},
        "breaking_wave_params": {
            "depth": 5.0,
            "angle": 160.0,
            "slope": 0.02
        }
    },
    "rockaways-beach": {
        "name": "Rockaways Beach, NY",
        "swell_buoy_id": "44065",
        "tide_station_id": "8516881",
        "wind_location": {"lat": 40.58, "lon": -73.82},
        "breaking_wave_params": {
            "depth": 5.0,
            "angle": 160.0,
            "slope": 0.02
        }
    },
    "belmar-beach": {
        "name": "Belmar Beach, NJ",
        "swell_buoy_id": "44091",
        "tide_station_id": "8532337",
        "wind_location": {"lat": 40.17, "lon": -74.01},
        "breaking_wave_params": {
            "depth": 5.0,
            "angle": 160.0,
            "slope": 0.02
        }
    },
    "steamer-lane": {
        "name": "Steamer Lane, CA",
        "swell_buoy_id": "46236",
        "tide_station_id": "9413450",
        "wind_location": {"lat": 36.95, "lon": -122.02},
        "breaking_wave_params": {
            "depth": 5.0,
            "angle": 160.0,
            "slope": 0.02
        }
    },
    "trestles-beach": {
        "name": "Trestles Beach, CA",
        "swell_buoy_id": "46277",
        "tide_station_id": "9410230",
        "wind_location": {"lat": 33.39, "lon": -117.58},
        "breaking_wave_params": {
            "depth": 5.0,
            "angle": 160.0,
            "slope": 0.02
        }
    }
}

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
    Get the full configuration for a specific surf spot.
    
    Args:
        spot_name (str): The slug/name of the surf spot.
        
    Returns:
        dict: The configuration dictionary for the spot, or None if not found.
    """
    return SURF_SPOTS_CONFIG.get(spot_name)

def get_all_locations():
    """
    Get a list of all supported location slugs.
    
    Returns:
        list: List of supported location slugs.
    """
    return list(SURF_SPOTS_CONFIG.keys())

def is_valid_location(location):
    """
    Check if a location is supported, handling both new slugs and legacy names.
    
    Args:
        location (str): Location name or slug to check.
        
    Returns:
        bool: True if location is supported, False otherwise.
    """
    location_lower = location.lower() if location else ""
    if location_lower in SURF_SPOTS_CONFIG:
        return True
    # Check if it's a legacy name that can be mapped
    return location_lower in LEGACY_LOCATION_MAP

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
        "met": config["swell_buoy_id"],  # Assuming met and swell are from the same buoy for now
        "tide": config["tide_station_id"]
    }

# Project Surf App: Gemini Context & MVP Plan

This document summarizes the analysis of the `surfpy` codebase and the agreed-upon plan for the Minimum Viable Product (MVP). It can be used to re-establish context in future sessions.

## 1. Codebase Analysis Summary

- **`surfdata.py`**: A Flask application that serves as the project's backend. It handles user authentication, surf session logging, and provides the API endpoints.
- **`ocean_data/`**: A Python package that acts as a high-level abstraction layer for fetching oceanographic data. It uses the `surfpy` library to get data for specific locations.
  - **`ocean_data/location.py`**: A key configuration file that maps human-readable location names to the data source IDs (buoys, tide stations) needed to fetch data. This will be enhanced for the MVP.
- **`surfpy/`**: A powerful, low-level library that is the core engine for all data fetching and processing. It interfaces directly with external services like NOAA.
  - **`surfpy/buoystation.py`**: Contains logic to fetch both real-time measurements and pre-packaged **forecast bulletins** from NDBC buoys.
  - **`surfpy/wavemodel.py`**: Contains more advanced logic to fetch raw **GRIB forecast data** directly from the GFS model, allowing for forecasts at any arbitrary location.
  - **`surfpy/tidestation.py`**: Contains logic to fetch **tide predictions** from the NOAA Tides and Currents API.

## 2. Key Concepts & Decisions

- **Historical vs. Forecast Data**: We've established that historical data comes from real-time measurement files from buoys, while forecast data originates from the GFS computer model. This is a standard and correct methodology.
- **Two Forecast Methods**:
  1.  **NOAA Bulletins (MVP Choice)**: A simple method that fetches pre-packaged, text-based forecast summaries for specific buoy locations. This is reliable and fast, making it ideal for the MVP.
  2.  **Direct GRIB Model**: A more complex but flexible method that fetches raw model data. This is a great candidate for a "Version 2" feature to expand location coverage.
- **Breaking Wave Height**: This is a critical calculation that translates abstract offshore swell data into a realistic surf height estimate for a specific spot. It uses the spot's `depth`, `angle`, and `slope` as inputs. We decided this is a **must-have feature for the MVP** because it provides the core value to the user.
- **Enthusiast User Focus**: The target user values detail and accuracy. The API and UI should provide both a simple summary (breaking wave height) for quick glances and the detailed underlying data (swell components) for deeper analysis.

## 3. MVP Plan: Forecast API Endpoint

### Feature Summary
We will build a new, cached API endpoint that accepts a surf spot's name and returns a detailed 7-day, hour-by-hour surf forecast.

- **Endpoint**: `/api/forecast/<spot_name>`
- **Method**: Use the simple and reliable **NOAA Bulletin** method.
- **Data**: The forecast will include a breaking wave height summary, detailed swell components, and merged wind and tide data for each hour.
- **Architecture**: The endpoint will be **cached** to ensure a fast user experience and will include robust error handling.

### High-Level Data Flow
1.  Request hits `/api/forecast/<spot_name>`.
2.  **Cache Check**: The system checks for a fresh (<1-2 hour old) cached forecast. If found, it's returned instantly.
3.  **Config Lookup**: If no fresh cache exists, the system looks up the spot's configuration (buoy ID, tide ID, breaking wave params) in `ocean_data/location.py`.
4.  **Fetch Data**: The system makes parallel calls to fetch the 7-day wave forecast (from NOAA bulletins), weather forecast (from `WeatherApi`), and tide forecast (from NOAA tide predictions).
5.  **Process & Combine**: The data is merged. The breaking wave height is calculated for each hour using the spot's specific parameters.
6.  **Format & Cache**: The final data is formatted into the specified JSON structure and stored in the cache.
7.  **Return**: The JSON response is returned to the user.

### API Response Structure
The API will return a list of hourly forecast objects, each with the following structure:
```json
{
  "timestamp": "2025-07-15T14:00:00Z",
  "breaking_wave_height": {
    "min": 2.5,
    "max": 4.0,
    "unit": "ft"
  },
  "swell_components": [
    {
      "height": 3.1,
      "period": 12,
      "direction": "SSE",
      "direction_degrees": 157,
      "unit": "ft"
    }
  ],
  "wind": {
    "speed": 12,
    "direction": "WNW",
    "unit": "mph"
  },
  "tide": {
    "height": 2.7,
    "unit": "ft"
  }
}
```

## 4. Implementation Details & Nuances

This section summarizes the specific steps taken and challenges encountered during the implementation of the forecast endpoint:

### a. `ocean_data/location.py` Updates
- The `LOCATION_TO_BUOYS` dictionary was replaced with `SURF_SPOTS_CONFIG` to hold comprehensive spot configurations (swell buoy, tide station, wind location, breaking wave parameters).
- Legacy functions (`get_buoys_for_location`, `is_valid_location`) were updated with mappings from old spot names to new slugs to maintain backward compatibility for existing endpoints.
- The `lido-beach` spot was added as a placeholder with `breaking_wave_params.depth` initially set to `20.0`.

### b. `ocean_data/forecast.py` Creation
- A new file `ocean_data/forecast.py` was created to house the `get_surf_forecast` function, orchestrating data fetching, merging, and processing.
- Initial implementation included fetching wave (bulletin), weather (WeatherApi), and tide data, merging them, and calculating breaking waves.

### c. `surfdata.py` Endpoint & Caching
- A new Flask endpoint `/api/forecast/<string:spot_name>` was added.
- `Flask-Caching` was integrated for simple in-memory caching to improve performance and reduce external API calls.
- The endpoint was protected with `@token_required`.

### d. Debugging & Refinements
- **Missing Dependency**: `Flask-Caching` was added to `requirements.txt` after an initial `FUNCTION_INVOCATION_FAILED` error on Vercel.
- **`isnan` Error**: Corrected `surfpy.tools.isnan` to `math.isnan` in `ocean_data/forecast.py`.
- **Breaking Wave Height Calculation**: The `breaking_wave_params.depth` for `lido-beach` was adjusted from `20.0` to `5.0` in `ocean_data/location.py` to yield more realistic breaking wave heights.
- **Swell Direction Discrepancy**: Investigated why the app's reported swell direction (from GFS Wave Model bulletin) differed from NDBC station page/Surfline. Concluded that the GFS Wave Model bulletin itself reports the direction (e.g., 351 degrees/NNW) and that other sources likely use different models or post-processing. The `direction_degrees` field was added to the API response for clarity.
- **Wind Data Alignment**: Identified that early wave forecast entries might lack wind data due to differing start times between NOAA bulletins and WeatherApi. (This specific fix was proposed but not yet implemented in the code).

## 4. Required Inputs For Next Steps

To continue development, I need the configuration for the initial 2-3 surf spots to be supported. Please provide the following for each spot:

```python
"spot-url-slug": {
    "name": "Human Readable Name, STATE",
    "swell_buoy_id": "NOAA_BUOY_ID",
    "tide_station_id": "NOAA_TIDE_STATION_ID",
    "wind_location": {"lat": 40.123, "lon": -73.123},
    "breaking_wave_params": {
        "depth": 5.0, # Updated to 5.0 for realism
        "angle": 160.0,
        "slope": 0.02
    }
}
```
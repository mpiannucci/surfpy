from typing import List
import requests
import datetime
import pytz

from . import units
from .location import Location
from .buoydata import BuoyData
from surfpy import buoydata


class WeatherApi():

    _API_ROOT_URL = 'https://api.weather.gov/'

    @staticmethod
    def points(location: Location) -> dict:
        # points API https://api.weather.gov/points/41.4302,-71.455
        url = f'{WeatherApi._API_ROOT_URL}points/{location.latitude:4f},{location.longitude:4f}'
        resp = requests.get(url)
        resp_json = resp.json()
        return resp_json['properties']

    @staticmethod
    def gridpoints(office: str, grid_x: int, grid_y: int) -> dict:
        # https://api.weather.gov/gridpoints/BOX/65,32
        url = f'{WeatherApi._API_ROOT_URL}gridpoints/{office}/{grid_x},{grid_y}'
        resp = requests.get(url)
        resp_json = resp.json()
        return resp_json['properties']

    @staticmethod
    def forecast(office: str, grid_x: int, grid_y: int) -> dict:
        # https://api.weather.gov/gridpoints/BOX/65,32/forecast
        url = f'{WeatherApi._API_ROOT_URL}gridpoints/{office}/{grid_x},{grid_y}/forecast'
        resp = requests.get(url)
        resp_json = resp.json()
        return resp_json['properties']

    @staticmethod
    def hourly_forecast(office: str, grid_x: int, grid_y: int) -> dict:
        # https://api.weather.gov/gridpoints/BOX/65,32/forecast/hourly
        url = f'{WeatherApi._API_ROOT_URL}gridpoints/{office}/{grid_x},{grid_y}/forecast/hourly'
        resp = requests.get(url)
        resp_json = resp.json()
        return resp_json['properties']
    
    @staticmethod
    def parse_weather_forecast(forecast_data: dict) -> List[BuoyData]:
        buoy_data = []

        if forecast_data is None:
            return buoy_data

        periods = forecast_data['periods']
        for period in periods:
            buoy_data_point = BuoyData(units.Units.english)
            buoy_data_point.date = datetime.datetime.strptime(period['startTime'], '%Y-%m-%dT%H:%M:%S%z').astimezone(pytz.utc)
            raw_temp = period['temperature']
            if raw_temp:
                buoy_data_point.air_temperature = int(raw_temp)
            buoy_data_point.short_forecast = period['shortForecast']
            raw_speed = period['windSpeed']
            if raw_speed:
                buoy_data_point.wind_speed = int(raw_speed.split(' ')[0])
            buoy_data_point.wind_compass_direction = period['windDirection']
            buoy_data_point.wind_direction =  units.direction_to_degree(buoy_data_point.wind_compass_direction)
            buoy_data.append(buoy_data_point)

        return buoy_data

    @staticmethod
    def fetch_hourly_forecast(location: Location) -> List[BuoyData]:
        meta = WeatherApi.points(location)
        raw_hourly = WeatherApi.hourly_forecast(meta['gridId'], meta['gridX'], meta['gridY'])
        return WeatherApi.parse_weather_forecast(raw_hourly)

    @staticmethod
    def fetch_hourly_forecast_from_metadata(meta: dict) -> List[BuoyData]:
        if not meta['gridId'] or not meta['gridX'] or not meta['gridY']:
            return []

        raw_hourly = WeatherApi.hourly_forecast(meta['gridId'], meta['gridX'], meta['gridY'])
        return WeatherApi.parse_weather_forecast(raw_hourly)

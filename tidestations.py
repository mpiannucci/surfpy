from .basestations import BaseStations
from .tidestation import TideStation
import json
try:
    import requests
except:
    pass

class TideStations(BaseStations):

    tide_stations_url = 'https://tidesandcurrents.noaa.gov/cgi-bin/map2/odinmap.cgi'

#payload = {"mode": "json", "nelat": "90", "nelng": "180", "swlat": "-90", "swlng": "-180"} 
#resp = requests.post(tide_stations_url, data=payload)

    def __init__(self):
        super(TideStations, self).__init__()
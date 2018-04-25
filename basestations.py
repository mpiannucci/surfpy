try:
    import requests
except:
    pass

class BaseStations(object):

    def __init__(self):
        self.fetch_date = None
        self.stations = []

    def parse_stations(self, raw_data):
        return False
    
    def fetch_stations(self, url):
        response = requests.get(self.active_buoys_url)
        if not len(response.text):
            return False
        return self.parse_stations(response.text)
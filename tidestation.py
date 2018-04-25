from .basestation import BaseStation


class TideStation(BaseStation):

    def __init__(self, station_id, location):
        super(TideStation, self).__init__(station_id, location)
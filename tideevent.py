from . import tidedata


class TideEvent(tidedata.TideData):

    class TidalEventType:
        high_tide='H'
        low_tide='L'

    def __init__(self, unit):
        super(TideEvent, self).__init__(unit)

        self.tidal_event = None

    @property
    def is_tidal_event(self):
        return self.tidal_event is not None
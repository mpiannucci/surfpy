from noaamodel import NOAAModel
from location import Location


class WaveModel(NOAAModel):

    _base_multigrid_url = 'http://nomads.ncep.noaa.gov:9090/dods/wave/mww3/{0}/{1}{0}_{2}.ascii?time[{5}:{6}],dirpwsfc.dirpwsfc[{5}:{6}][{3}][{4}],htsgwsfc.htsgwsfc[{5}:{6}][{3}][{4}],perpwsfc.perpwsfc[{5}:{6}][{3}][{4}],swdir_1.swdir_1[{5}:{6}][{3}][{4}],swdir_2.swdir_2[{5}:{6}][{3}][{4}],swell_1.swell_1[{5}:{6}][{3}][{4}],swell_2.swell_2[{5}:{6}][{3}][{4}],swper_1.swper_1[{5}:{6}][{3}][{4}],swper_2.swper_2[{5}:{6}][{3}][{4}],ugrdsfc.ugrdsfc[{5}:{6}][{3}][{4}],vgrdsfc.vgrdsfc[{5}:{6}][{3}][{4}],wdirsfc.wdirsfc[{5}:{6}][{3}][{4}],windsfc.windsfc[{5}:{6}][{3}][{4}],wvdirsfc.wvdirsfc[{5}:{6}][{3}][{4}],wvhgtsfc.wvhgtsfc[{5}:{6}][{3}][{4}],wvpersfc.wvpersfc[{5}:{6}][{3}][{4}]'

    def create_url(self, location, start_time_index, end_time_index):
        timestamp = self.latest_model_time()
        datestring = timestamp.strftime('%Y%m%d')
        hourstring = timestamp.strftime('%Hz')

        lat_index, lon_index = self.location_index(location)
        url = self._base_multigrid_url.format(datestring, self.name, hourstring, lat_index, lon_index, start_time_index, end_time_index)
        return url

def east_coast_wave_model():
    return WaveModel('multi_1.at_10m', 'Multi-grid wave model: US East Coast 10 arc-min grid', Location(0.00, 260.00), Location(55.00011, 310.00011), 0.167, 0.125)
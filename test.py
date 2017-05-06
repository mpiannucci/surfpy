from buoystations import BuoyStations

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cm


class BuoyPlots(object):

    def __init__(self):
        _stations = BuoyStations()
        _stations.fetch_buoy_stations()

        self.stations = {}
        for station in _stations.stations:
            self.stations[station.station_id] = station

    def fetch_buoy_data(self, station_id, count):
        return self.stations[station_id].fetch_wave_spectra_reading(count)

    def plot_directional_spectra(self, station_id):
        if len(self.stations[station_id].data) < 1:
            return

        fig = plt.figure(figsize=(6, 6), dpi=100)
        ax = fig.add_subplot(111, projection='polar')
        ax.set_title('Station ' + station_id + ': Directional Wave Spectra\n')
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        bars = ax.bar(self.stations[station_id].data[0].wave_spectra.radian_angle, self.stations[station_id].data[0].wave_spectra.energy, align='center', linewidth=1.0)
        norm = colors.Normalize(vmin=self.stations[station_id].data[0].wave_spectra.frequency[0], vmax=self.stations[station_id].data[0].wave_spectra.frequency[-1])
        cmap = cm.jet_r
        colormap = cm.ScalarMappable(norm=norm, cmap=cmap)
        for freq, energy, bar in zip(self.stations[station_id].data[0].wave_spectra.frequency, self.stations[station_id].data[0].wave_spectra.energy, bars):
            bar.set_facecolor(colormap.to_rgba(freq))
            bar.set_edgecolor(colormap.to_rgba(freq))
            bar.set_alpha(0.3)
        plt.show()
        plt.clf()

    def plot_wave_energy(self, station_id):
        if len(self.stations[station_id].data) < 1:
            return

        swell_indexes = [self.stations[station_id].data[0].wave_spectra.period[i] for i in [x._frequency_index for x in self.stations[station_id].data[0].swell_components]]
        swell_energies = [x._max_energy for x in self.stations[station_id].data[0].swell_components]

        ax = plt.subplot(111)
        ax.set_title('Station ' + station_id + ': Wave Spectra\n')
        ax.set_xlim(0.0, 20.0)
        ax.set_xticks([0.0, 3.0, 6.0, 9.0, 12.0, 15.0, 18.0, 21.0])
        ax.plot(self.stations[station_id].data[0].wave_spectra.period, self.stations[station_id].data[0].wave_spectra.energy)
        ax.scatter(swell_indexes, swell_energies)
        ax.set_ylim(bottom=0.0)
        plt.grid()
        plt.show()
        plt.clf()

if __name__ == '__main__':
    plots = BuoyPlots()
    plots.fetch_buoy_data('44097', 1)
    plots.plot_directional_spectra('44097')
    plots.plot_wave_energy('44097')
import math
from . import tools
from .units import Units, degree_to_direction
from .swell import Swell


class BuoySpectra(object):

    def __init__(self, frequency=None, energy=None, angle=None, seperation_frequency=float('nan')):
        self.frequency = frequency
        if self.frequency is None:
            self.frequency = []
        self.energy = energy
        if self.energy is None:
            self.energy = []
        self.angle = angle
        if self.angle is None:
            self.angle = []
        self.seperation_frequency = seperation_frequency

    @property
    def average_period(self):
        zero_moment = 0.0
        second_moment = 0.0

        if len(self.frequency) < 1 or len(self.energy) < 1:
            return float('nan')

        for i in range(0, len(self.frequency)):
            bandwidth = 0.01
            if i > 0:
                bandwidth = abs(self.frequency[i] - self.frequency[i-1])
            else:
                bandwidth = abs(self.frequency[i+1] - self.frequency[i])

            zero_moment += tools.zero_spectral_moment(self.energy[i], bandwidth)
            second_moment += tools.second_spectral_moment(self.energy[i], bandwidth, self.frequency[i])

        return math.sqrt(zero_moment/second_moment)

    @property
    def wave_summary(self):
        if len(self.frequency) < 1 or len(self.energy) < 1:
            return None

        # Calculate the Significant wave height over the entire spectra
        # And find the dominant frequency index
        max_energy_index = -1
        max_energy = -1.0
        zero_moment = 0.0

        for i in range(0, len(self.frequency)):
            bandwidth = 0.01
            if i > 0:
                bandwidth = abs(self.frequency[i] - self.frequency[i-1])
            else:
                bandwidth = abs(self.frequency[i+1] - self.frequency[i])

            zero_moment += tools.zero_spectral_moment(self.energy[i], bandwidth)

            if self.energy[i] > max_energy:
                max_energy = self.energy[i]
                max_energy_index = i

        primary_swell = Swell(Units.metric)
        primary_swell.wave_height = 4.0 * math.sqrt(zero_moment)
        primary_swell.period = 1.0 / self.frequency[max_energy_index]
        primary_swell.direction = self.angle[max_energy_index]
        primary_swell.compass_direction = degree_to_direction(primary_swell.direction)
        return primary_swell

    @property
    def swell_components(self):
        if len(self.frequency) < 1 or len(self.energy) < 1:
            return []

        min_indexes, min_values, max_indexes, max_values = tools.peakdetect(self.energy, delta=0.05)

        components = []
        prev_index = 0
        for i in range(0, len(max_values)):
            min_index = prev_index
            if i >= len(min_indexes):
                min_index = len(self.energy)
            else:
                min_index = min_indexes[i]

            zero_moment = 0.0
            for j in range(prev_index, min_index):
                bandwidth = 0.01
                if j > 0:
                    bandwidth = abs(self.frequency[j] - self.frequency[j-1])
                else:
                    bandwidth = abs(self.frequency[j+1] - self.frequency[j])

                zero_moment += tools.zero_spectral_moment(self.energy[j], bandwidth)

            component = Swell(Units.metric)
            component.wave_height = 4.0 * math.sqrt(zero_moment)
            component.period = 1.0 / self.frequency[max_indexes[i]]
            component.direction = self.angle[max_indexes[i]]
            component.compass_direction = degree_to_direction(component.direction)
            component.max_energy = max_values[i]
            component.frequency_index = max_indexes[i]
            components.append(component)

            prev_index = min_index

        components.sort(key=lambda x: x.max_energy, reverse=True)
        return components

    @property
    def period(self):
        return list(map(lambda x: float(1.0/float(x)), self.frequency))

    @property
    def radian_angle(self):
        return list(map(lambda x: float(x) * (math.pi/180.0), self.angle))

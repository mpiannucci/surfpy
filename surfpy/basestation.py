class BaseStation(object):

    def __init__(self, station_id, location):
        self.station_id = station_id
        self.location = location
        self.name = ''
        self._parse_name()
    
    def _parse_name(self):
        if self.location.name == '':
            return

        self.name = ''

        if '-' in self.location.name:
            components = self.location.name.split('-')
            for comp in components:
                if not comp.strip().isdigit():
                    self.name += ' ' + comp
        else:
            self.name = self.location.name

        if '(' in self.name:
            self.name = self.name.split('(')[0]

        if 'NM' in self.name:
            components = self.name.split(' ')
            self.name = ''
            for comp in components:
                if 'NM' in comp:
                    break
                elif comp.strip().isdigit():
                    break
                if len(self.name) > 0:
                    self.name += ' '
                self.name += comp

        self.name = self.name.strip().title()
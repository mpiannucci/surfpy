class BaseData(object):

    def __init__(self, unit):
        self.unit = unit

    def change_units(self, new_units):
        self.unit = new_units
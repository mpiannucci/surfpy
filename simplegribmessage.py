import grippy
from location import Location


class SimpleGribMessage(grippy.Message):

    @property
    def hour(self):
        return self.sections[3].template.forecast_time

    @property
    def var(self):
        return self.sections[self.PRODUCT_DEFINITION_SECTION_INDEX].template.parameter_number.abbrev

    @property
    def is_array_var(self):
        return self.sections[self.PRODUCT_DEFINITION_SECTION_INDEX].template.first_fixed_surface_type_value == 241

    @property
    def var_index(self):
        if not self.is_array_var:
            return -1
        return self.sections[self.PRODUCT_DEFINITION_SECTION_INDEX].template.first_fixed_surface_scaled_value

    @property
    def lat_count(self):
        return self.sections[self.GRID_DEFINITION_SECTION_INDEX].template.meridian_point_count

    @property 
    def lon_count(self):
        return self.sections[self.GRID_DEFINITION_SECTION_INDEX].template.parallel_point_count

    @property
    def start_lat(self):
        return self.sections[self.GRID_DEFINITION_SECTION_INDEX].template.start_latitude

    @property
    def start_lon(self):
        return self.sections[self.GRID_DEFINITION_SECTION_INDEX].template.start_longitude

    @property
    def lat_step(self):
        return self.sections[self.GRID_DEFINITION_SECTION_INDEX].template.meridian_point_count

    @property
    def lon_step(self):
        return self.sections[self.GRID_DEFINITION_SECTION_INDEX].template.parallel_point_count

    @property
    def end_lat(self):
        return self.sections[self.GRID_DEFINITION_SECTION_INDEX].template.end_latitude

    @property
    def end_lon(self):
        return self.sections[self.GRID_DEFINITION_SECTION_INDEX].template.end_longitude

    @property
    def lat_indices(self):
        start = self.start_lat
        step = self.lat_step
        count = self.lat_count
        return list([start + x*step for x in range(0, count+1)])

    @property
    def lon_indices(self):
        start = self.start_lon
        step = self.lon_step
        count = self.lon_count
        return list([start + x*step for x in range(0, count+1)])

    @property
    def data(self):
        return self.sections[self.DATA_SECTION_INDEX].all_scaled_values(self.sections[self.BITMAP_SECTION_INDEX].all_bit_truths)

    def location_for_index(self, index):
        if index >= self.lat_count*self.lon_count:
            return Location(float('NaN'), float('NaN'), 'invalid')

        lat_index = int(index/self.lat_count)
        lon_index = index % self.lat_count

        return Location(self.start_lat + (lat_index*self.lat_step), self.start_lon + (lon_index*self.lon_step))


def read_simple_grib_messages_raw(all_data, count=-1):
    messages = []

    offset = 0
    while offset < len(all_data):
        messages.append(SimpleGribMessage(all_data, offset))
        offset = offset + messages[-1].length

        if count > 0 and len(messages) == count:
            break

    return messages

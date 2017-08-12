import grippy


class WaveGribMessage(grippy.Message):

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
        return None

    @property
    def lon_indices(self):
        return None

    @property
    def data(self):
        return self.sections[self.DATA_SECTION_INDEX].all_scaled_values(self.sections[self.BITMAP_SECTION_INDEX].all_bit_truths)
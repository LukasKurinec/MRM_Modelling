from liab.grouped_inputs import GrouppedInputs


class Mortality(GrouppedInputs):
    def __init__(self, filename='mortality', separator=',', index_col=None):
        super().__init__(filename, separator=separator, index_col=index_col)

    def add_extra_optional_data(self):
        """
        We have the option to add extra columns to a specific input table in run-time with functions
        """
        pass

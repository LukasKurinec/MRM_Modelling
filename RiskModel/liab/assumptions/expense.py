from liab.grouped_inputs import GrouppedInputs


class Expense(GrouppedInputs):
    def __init__(self, filename='expense', separator=',', index_col=None):
        super().__init__(filename, separator=separator, index_col=index_col)

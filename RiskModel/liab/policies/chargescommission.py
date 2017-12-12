from liab.grouped_inputs import GrouppedInputs


class ChargesCommission(GrouppedInputs):
    def __init__(self, filename='chargescommission', separator=',', index_col=None):
        super().__init__(filename, separator=separator, index_col=index_col)

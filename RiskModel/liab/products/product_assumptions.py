from liab.grouped_inputs import GrouppedInputs


class ProductAssumptions(GrouppedInputs):
    def __init__(self, filename='productassumptions', separator=',', index_col=0):
        super().__init__(filename, separator=separator, index_col=index_col)

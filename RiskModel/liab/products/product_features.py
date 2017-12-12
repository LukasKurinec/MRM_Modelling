from liab.grouped_inputs import GrouppedInputs


class ProductFeatures(GrouppedInputs):
    def __init__(self, filename='productfeatures', separator=',', index_col=0):
        super().__init__(filename, separator=separator, index_col=index_col)

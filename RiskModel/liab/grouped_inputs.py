from liab.general import look_for_in_df
from liab.general import open_csvfile
from liab.general import change_value_in_df


class GrouppedInputs:
    def __init__(self, filename, separator=',', index_col=None):
        self.df = open_csvfile(filename, separator=separator, index_col=index_col)

    def look_for(self, category, line=None, index=None, label=None):
        """
        searching input tables
        :param category: column names, text
        :param line: number begins with 1 for non-indexed rows
        :param index: number begins with 0 for non-indexed rows
        :param label: text for indexed rows
        :return: the value for a given category and index/line/label
        """
        result = "Not found"
        if line:
            result = look_for_in_df(self.df, category, line - 1)
        elif index or index == 0:
            result = look_for_in_df(self.df, category, index)
        elif label:
            result = look_for_in_df(self.df, category, label)
        return result

    def get_as_dictionary(self):
        return self.df.to_dict()

    def change_value(self, category, value, label=None, line=None, age=None):
        """
        changing values in input tables
        :param category: column names, text
        :param value: change value to this value
        :param label: text for indexed rows
        :param line: number begins with 1 for non-indexed rows
        :param age: number begins with 0 for non-indexed rows
        """
        if label:
            change_value_in_df(self.df, category, label, value)
        elif line:
            change_value_in_df(self.df, category, line - 1, value)
        elif age:
            change_value_in_df(self.df, category, age, value)

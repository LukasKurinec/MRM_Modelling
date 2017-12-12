from math import trunc
from liab.general import dict_to_series
from liab.general import dict_to_df
from liab.general import look_for_in_df


class Frame:
    def __init__(self, step_until, step_size, month, age_x, valuation_date):
        self.step_until = step_until
        self.step_size = step_size
        self.month = month
        self.age_x = age_x
        self.valuation_date = valuation_date
        self.dictionary = self.table()
        self.df = self.dict_to_df()

    @staticmethod
    def calc_ypol(month):
        return trunc(((month - 1) / 12) + 1)

    @staticmethod
    def calc_age_x(month, age_x):
        return trunc(age_x + month / 12)

    def table(self):
        dictionary = {0: ['0', self.month, self.calc_ypol(self.month), self.calc_age_x(self.month, self.age_x)]}
        for step in range(self.step_size, self.step_until, self.step_size):
            dictionary[step] = [(str(step) + ' - ' + str(step - self.step_size)), self.month + step,
                                self.calc_ypol(self.month + step), self.calc_age_x(self.month + step, self.age_x)]
        return dictionary

    def show_table(self):
        for key, value in self.dictionary.items():
            print(key, value)

    def dict_to_series(self):
        series = dict_to_series(self.dictionary)
        return series

    def dict_to_df(self):
        df = dict_to_df(self.dictionary, orient='index')
        df.columns = ['step', 'month', 'ypol', 'age_x']
        return df

    def look_for(self, category, line=None, index=None, label=None):
        """
        searching input tables
        :param category: column names, text
        :param line: number begins with 1 for non-indexed rows
        :param index: number begins with 0 for non-indexed rows
        :param label: text for indexed rows
        :return: the value for a given category and age/line/label
        """
        result = "Not found"
        if line:
            result = look_for_in_df(self.df, category, line - 1)
        elif index or index == 0:
            result = look_for_in_df(self.df, category, index)
        elif label:
            result = look_for_in_df(self.df, category, label)
        return result

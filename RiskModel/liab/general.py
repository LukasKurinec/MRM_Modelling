"""
The aim of the general module is mainly for developer helping purposes
"""

import pandas as pd
import sys
import os


def open_csvfile(name, index_col=None, skiprows=None, usecols=None, separator=','):
    """
    reading csv files
    :param name: file name (without .csv extension)
    :param index_col: number of index column
    :param skiprows: don't read the first X rows (requires a number)
    :param usecols: read only given columns (requires a list of number, like [0,1,2])
    :param separator: what separator to use, text e.g. '\t'
    :return: Pandas DataFrame
    """
    df = pd.read_csv('inputfiles/' + name + '.csv', skiprows=skiprows, usecols=usecols, sep=separator,
                     index_col=index_col).fillna(0)
    df.columns = df.columns.str.lower()
    return df


def write_to_excel(df, filename):
    """
    write one sheet into an excel file
    :param df: must be Pandas DataFrame
    :param filename: path/filename (without extension)
    """
    df.to_excel(filename + '.xlsx')


def dict_to_series(dictionary):
    series = pd.Series(dictionary)
    return series


def dict_to_df(dictionary, orient='column'):
    """
    create a Pandas DataFrame from dictionary
    :param dictionary: the dictionary
    :param orient: column or index, column is the default
    :return: Pandas DataFrame
    """
    df = pd.DataFrame.from_dict(dictionary, orient=orient)
    return df


def look_for_in_df(df, category, line):
    """
    searching within a Pandas DataFrame
    :param df: must be a Pandas DataFrame
    :param category: column name, text
    :param line: number of line or label
    :return: the value for a given category and age
    """
    try:
        return df.loc[line, category]
    except KeyError:
        print("couldn't locate \"" + str(category) + "\"")


def change_value_in_df(df, category, line, value):
    """
    change a value within a Pandas DataFrame
    :param df: must be a Pandas DataFrame
    :param category: column name, text
    :param line: row number or indexed label
    :param value: change to
    """
    try:
        df.loc[line, category] = value
    except:
        print("Unexpected error:", sys.exc_info()[0])

def connectMySQL():
    """ storing connection parameters in source code only suitable for testing """
    try:
        import MySQLdb

        user = ''
        pw = ''
        host = ''
        db = ''

        conn = MySQLdb.connect(host=host, user=user, passwd=pw, db=db)
        c = conn.cursor()

        return c, conn
    except Exception as e:
        return str(e)


# Disable
def blockPrint():
    sys.stdout = open(os.devnull, 'w')


# Restore
def enablePrint():
    sys.stdout = sys.__stdout__

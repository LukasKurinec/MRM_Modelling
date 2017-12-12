"""
The aim of the utility module is mainly for business user helping purposes
"""

from copy import deepcopy
import time


def timeit_start():
    current_time = time.time()
    return current_time


def timeit_stop(last_time, task):
    """
    Print out the time difference between last timeit_start() function and timeit_stop() function
    :param last_time: timeit_start value
    E.g. 'starttime = utility.timeit_start()'
    Call funtions here what you want to measure
    Then close with 'utility.timeit_stop(starttime, "Calculation")'
    :param task: Must be text, user defined name for task between timeit start and stop functions
    """
    print(task + ' took {} seconds'.format(round(time.time() - last_time, 3)))


def copy(object):
    return deepcopy(object)

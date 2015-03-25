from __future__ import division, print_function

__all__ = ['Monitor']


class Monitor(object):
    """
    Instantiates objects to monitor a given simulation.

    """

    def __init__(self):
        pass


def record(ts, msg, to=None):
    if to is None:
        print.info("[{:8.2f} days] {}".format(ts, msg))
    else:
        to.append("[{:8.2f} days] {}".format(ts, msg))

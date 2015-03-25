from __future__ import division

import simpy
from numpy import random

from util import SimpyMixin

__all__ = ['User']


USER_LEVELS = ['admin', 'priviledged', 'basic']
USER_LEVEL_FREQUENCIES = [0.07, 0.13, 0.8]


class User(SimpyMixin, object):
    """
    A network user.

    """
    def __init__(self, network, level=None, proficiency=0.1, shift_start=8, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        self.network = network

        if level is None or level not in USER_LEVELS:
            level = random.choice(USER_LEVELS, p=USER_LEVEL_FREQUENCIES)
        self.level = level

        self.working = self.process(self.work(shift_start=shift_start))

    def work(self, shift_start):

        # initial offset to account for time people take to start working
        _ = yield self.timeout(shift_start / 24)

        while True:
            _ = yield self.network.users.put(self)
            _ = yield self.timeout(8)
            _ = yield self.network.users.get(filter=lambda u: u==self)
            _ = yield self.timeout(16)

from __future__ import division

import simpy
from networkx import Graph
from numpy import random

from util import pluralize, snake_case, SimpyMixin

__all__ = ['Network', 'Router', 'Server', 'Subnet', 'Sensor']


class Network(object):
    """
    Network object contains network items and a reference to the administrator.

    """

    def __init__(self, items=None, admin=None):
        self.all_items = [] if items is None else items
        self.admin = admin

        # Groups items under attrs with the snake_case plural form of the item class
        for item in self.all_items:
            setattr(item, 'network', self)

            if admin is not None:
                setattr(item, 'admin', self)
                if hasattr(self.admin, 'env'):
                    setattr(item, 'env', self.admin.env)

            item_type = snake_case(pluralize(item.__class__.__name__))

            if hasattr(self, item_type):
                getattr(self, item_type).append(item)
            else:
                setattr(self, item_type, [item])


class Networked(object):
    def __init__(self, name=None, *args, **kwargs):
        self.name=name

    def __repr__(self):
        return "<{}>".format(self.name)


class Vulnerable(SimpyMixin, Networked):
    def __init__(self, *args, **kwargs):
        super(Vulnerable, self).__init__(*args, **kwargs)
        self.vulnerabilities = self.filter_store()


class Subnet(Vulnerable):
    def __init__(self, **kwargs):
        super(Subnet, self).__init__(**kwargs)


class Server(Vulnerable):
    def __init__(self, **kwargs):
        super(Server, self).__init__(**kwargs)


class Router(Vulnerable):
    def __init__(self, **kwargs):
        super(Router, self).__init__(**kwargs)


class Sensor(SimpyMixin, Networked):
    """
    A network sensor, e.g., intrusion detection software (IDS).

    :param env: simulation environment
    :param monitoring: list of items being monitored
    :param false_alarm_rate: average number of days between false alarms (lambda parameter for exponential distribution)

    :func false_alarm: process for creating false alarms on a periodic basis

    """

    def __init__(self, monitoring=None, false_alarm_rate=10, *args, **kwargs):
        super(Sensor, self).__init__(*args, **kwargs)
        self.alarm = self.filter_store()
        self.false_alarm_rate = false_alarm_rate
        self.monitored_items = self.filter_store()

        if monitoring:
            for item in monitoring.items:
                self.monitoring.put(item)

        self.false_warning = self.process(self.false_alarm())

    def __repr__(self):
        return '<{}>'.format(self.name if self.name is not None else 'Sensor X')

    def false_alarm(self):
        while True:
            yield self.timeout(random.exponential(self.false_alarm_rate))
            self.alarm.put({'ts': self.now,
                            'sensor': self,
                            'system': None})

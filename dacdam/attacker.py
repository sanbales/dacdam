from __future__ import division

import simpy
from numpy import random

__all__ = ['Attacker', 'Malware']


NOMINAL_TIME_TO_LEARN = 10


class Attacker(SimpyMixin, object):
    """
    A cyber attacker entity.

    :param env:
    :param competency:
    :param associates:

    :type env:
    :type competency:
    :type associates:

    :func scan:
    :func attack:

    """
    def __init__(self, competency=0.5, associates=None,
                 vulnerability_manager=None, known_vulnerabilities=None, *args, **kwargs):

        super(Attacker, self).__init__(*args, **kwargs)

        self.competency = competency
        self.associates = [] if associates is None else associates
        self.vulnerability_manager = vulnerability_manager

        self.targets = self.filter_store()
        self.known_vulnerabilities = self.filter_store()

        if instance(known_vulnerabilities, list):
            for vulnerability in known_vulnerabilities:
                _ = yield self.known_vulnerabilities(vulnerability)

        self.scanning = self.process(self.scan())
        self.attacking = self.process(self.attack())
        self.learning = self.process(self.learn())

    def scan(self):
        """ Scan for potential targets. """
        while True:
            # Scan for a target

    def attack(self, target):
        """ Attack a target """
        while True:
            pass
            #

    def learn(self):
        """ Learn new vulnerabilities """
        while True:
            _ = yield self.timeout(NOMINAL_TIME_TO_LEARN / self.competence ** 4)
            zero_days = [v for v in self.vulnerability_manager.vulnerabilities.items if v.zero_day]
            _ = yield self.process(add_vulnerability(random.choice(zero_days)))

    def add_vulnerability(self, vulnerability):
        _ = yield self.known_vulnerabilities.put(vulnerability)


class Malware(SimpyMixin, object):
    """
    Malware that can spread through a network (e.g., virus, trojan, worm).

    :param owner: attacker that owns the malware
    :param controllable: whether or not the malware is controllable by the owner

    :type owner: :class:`dacdam.attacker.Attacker`
    :type controllable: bool

    """
    def __init__(self, owner=None, controllable=False, *args, **kwargs):
        super(Malware, self).__init__(*args, **kwargs)

        self.owner = owner
        self.controllable = controllable

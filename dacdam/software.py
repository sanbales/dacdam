from __future__ import division

import simpy
from numpy import random

from util import SimpyMixin

__all__ = ['VulnerabilityManager', 'Vulnerability', 'Patch', 'Service']


## VULNERABILITY STATES AND AVERAGE TIME (EXP FXN) TO TRANSITION TO NEXT STATE
VULNERABILITY_STATES = [
    {'name': 'UNDISCOVERED',
     'lambda': 90,
     'zero_day': True},
    {'name': 'IDENTIFIED',
     'lambda': 30},
    {'name': 'PATCHED',
     'patched': True}]


class VulnerabilityManager(SimpyMixin, object):
    """
    Store for vulnerabilities and patches.

    :param env: simulation environment
    :param num_vulnerabilities: number of vulnerabilities to create when manager is initiated

    :type env: :class:`simpy.Environment`
    :type num_vulnerabilities: int

    """
    def __init__(self, num_vulnerabilities=0, *args, **kwargs):
        super(VulnerabilityManager, self).__init__(*args, **kwargs)

        self.vulnerabilities = self.filter_store()
        self.patches = self.filter_store()

        for i in range(num_vulnerabilities):
            Vulnerability(env=self.env,
                          publish_patch_to=self.patches,
                          publish_self_to=self.vulnerabilities)


class Vulnerability(SimpyMixin, object):
    """
    A system vulnerability that could be exploited by an attacker

    :param name: name
    :param state: state of the vulnerability
    :param activities_supported: list of activities that can be supported by the vulnerability
    :param time_to_process: time it takes to transition the vulnerability between VulnerabilityState
    :param publish_patch_to: store to publish patches to
    :param publish_self_to: store to which to publish itself

    :type env: :class:`simpy.Environment`
    :type publish_patch_to: :class:`simpy.Store`
    :type publish_self_to: :class:`simpy.Store`

    """

    def __init__(self, name=None, state=0, activities_supported=None, publish_patch_to=None,
                 publish_self_to=None, affects=None, *args, **kwargs):

        super(Vulnerability, self).__init__(*args, **kwargs)

        if name is None and publish_self_to is not None:
            self.name = 'VUL{:04d}'.format(len(publish_self_to.items) + 1)
        else:
            self.name = name if name else 'VULXXXX'

        self.state_id = 0 if state is None else state

        self.activities_supported = activities_supported if activities_supported is not None else []
        self.affects = affects
        if self.affects is None:
            self.affects = random.choice(['Server', 'Subnet', 'Router'], p=[0.3, 0.1, 0.6])

        self.publish_patch_to = publish_patch_to
        self.publish_self_to = publish_self_to

        self.evolving = self.process(self.evolve())

        if self.publish_self_to is not None:
            self.publish_self_to.put(self)

    def __repr__(self):
        return "<Vulnerability: {} [{}]>".format(self.name, self.state)

    @property
    def state(self):
        return VULNERABILITY_STATES[self.state_id].get('name', 'UNDESIGNATED')

    @property
    def p_lambda(self):
        return VULNERABILITY_STATES[self.state_id].get('lambda', None)

    @property
    def zero_day(self):
        return VULNERABILITY_STATES[self.state_id].get('zero_day', False)

    @property
    def patched(self):
        return VULNERABILITY_STATES[self.state_id].get('patched', False)

    def evolve(self):
        """ Evolves a vulnerability through the possible states """
        while not self.patched:
            yield self.timeout(random.exponential(self.p_lambda))
            self.state_id += 1
            if self.state_id == (len(VULNERABILITY_STATES) - 1):
                self.publish_patch_to.put(Patch(removes=self))


class Patch(object):
    """
    A patch for a set of vulnerabilities that may introduce other vulnerabilities.

    :param removes: list of vulnerabilities to remove
    :param avg_new_vulnerabilities: lambda for poisson distribution for number of vulnerabilities created per patch

    :type removes: list
    :type avg_new_vulnerabilities: float

    """

    def __init__(self, removes=None, avg_new_vulnerabilities=0.25):
        self.removes = [] if removes is None else removes
        if isinstance(removes, Vulnerability):
            self.removes = [removes]

        names = [vul.name for vul in self.removes]
        v0 = self.removes[0]

        self.adds = []
        for i in range(random.poisson(avg_new_vulnerabilities)):
            self.adds.append(Vulnerability(env=v0.env,
                                           publish_patch_to=v0.publish_patch_to,
                                           publish_self_to=v0.publish_self_to,
                                           affects=v0.affects))

    def __repr__(self):
        return '<Patch for {}>'.format(', '.join([r.name for r in self.removes]))


class Service(SimpyMixin, object):
    """
    A software service.

    :param name: name of the service

    :type name: str

    """

    def __init__(self, name=None, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)
        self.name = 'Service' if name is None else name

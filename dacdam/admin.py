from __future__ import division

import simpy
from numpy import random

from software import Vulnerability, VULNERABILITY_STATES
from network import Network, Router, Server, Subnet, Sensor, Vulnerable

from util import SimpyMixin

__all__ = ['NetworkAdministrator']


class NetworkAdministrator(SimpyMixin, object):
    """
    The Network Administrator entities manage networks.

    :param env: simulation environment
    :param name: name of the network administrator
    :param network_items: list of items to put in the network monitored
    :param vulnerabilities: store of vulnerabilities
    :param patches: store of patches ready to be applied
    :param patching_period: average time between patches (in days) for exponential distribution
    :param upgrade_period: average time between upgrades (in days) for exponential distribution
    :param alarm_scan: period for scanning alarm
    :param vul_per_upgrade: average number of vulnerabilities added in each uprade for poisson distribution
    :param id_vulnerability: probability administrator identifies vulnerability used in discovered attack

    :type env: :class:`simpy.Environment`
    :type name: str
    :type network_items: list
    :type vulnerabilities: :class:`simpy.Store`
    :type patches: :class:`simpy.Store`
    :type patching_period: float
    :type upgrade_period: float
    :type alarm_type: float
    :type vul_per_upgrade: float
    :type id_vulnerability: float

    :func monitor: monitor the network sensors
    :func upgrade: upgrade (or add new applications) to networked systems
    :func patch: the process admins follow after patching period
    :func apply-patch:
    :func add_vulnerability:
    :func remove_vulnerability:

    """

    def __init__(self, name=None, network_items=None, vulnerabilities=None, patches=None,
                 patching_period=15., upgrade_period=30., alarm_scan=1/24./60., vul_per_upgrade=3,
                 id_vulnerability=0.1, *args, **kwargs):

        super(NetworkAdministrator, self).__init__(*args, **kwargs)

        self.name = name if name else 'NetworkAdmin'
        self.network = Network(items=network_items, admin=self)
        self.patches = patches
        self.vulnerabilities = vulnerabilities
        self.patching_period = patching_period
        self.upgrade_period = upgrade_period
        self.alarm_scan = alarm_scan
        self.vul_per_upgrade = vul_per_upgrade
        self.id_vulnerability = id_vulnerability

        self.num_patches_applied = 0

        self.alarms = {'new': self.filter_store(),
                       'old': self.filter_store()}

        # Register sensors to its 'new' alarms store
        for network_item in self.network.all_items:
            if isinstance(network_item, Sensor):
                network_item.alarm = self.alarms['new']

        self.patching = self.process(self.patch())
        self.monitoring = self.process(self.monitor())
        self.upgrading_servers = self.process(self.upgrade(item_type=Server))
        self.upgrading_routers = self.process(self.upgrade(item_type=Router))
        self.upgrading_subnets = self.process(self.upgrade(item_type=Subnet))

    def __repr__(self):
        return "<{}>".format(self.name)

    def patch(self):
        """
        The patching process the Network Administrators follow.

        """

        while self.patches is not None:
            yield self.timeout(random.exponential(self.patching_period))
            new_patches = self.patches.items[self.num_patches_applied:]
            for patch in new_patches:
                self.apply_patch(patch)
            self.num_patches_applied = len(self.patches.items)

    def apply_patch(self, patch):
        """
        Applies the patch of interest to the relevant systems in the network.

        :param patch: the patch to be applied
        :type patch: :class:`dacdam.software.Patch`

        """

        vulnerabilities_added = set()

        for item in [item for item in self.network.all_items if isinstance(item, Vulnerable)]:
            for vulnerability in patch.removes:
                self.process(self.remove_vulnerability(vulnerability, item))

            for vulnerability in patch.adds:
                vulnerabilities_added.add(vulnerability.name)
                self.process(self.add_vulnerability(vulnerability))

    def monitor(self):
        """
        The alarm monitoring process the Network Administrators follow.

        """

        while True:
            alarm = yield self.alarms['new'].get()

            # TODO: COMPLETE THE PROCESSING OF THE ALARMS
            for vulnerability in alarm.get('vulnerabilities', []):
                if random.uniform(0,1) < self.id_vulnerability and \
                   vulnerability.zero_day:
                    vulnerability.action.succeed()

            self.alarms['old'].put(alarm)

    def upgrade(self, item_type=None, time_to_upgrade=None):
        """
        The software upgrade process the Network Administrators follow.

        This process primarily adds vulnerabilities and emulates having new software being added to the network systems.

        """

        if item_type is None:
            item_type = random.choice(['Server', 'Subnet', 'Router'],
                                      p=[0.6, 0.05, 0.35])
        items = [item for item in self.network.all_items if isinstance(item, item_type)]
        while items:
            _ = yield self.timeout(self.upgrade_period)
            num_new_vulnerabilities = random.poisson(self.vul_per_upgrade)
            for i in range(num_new_vulnerabilities):
                vulnerability = Vulnerability(env=self.env,
                                              publish_patch_to=self.patches,
                                              publish_self_to=self.vulnerabilities)
                self.process(self.add_vulnerability(vulnerability))

    def add_vulnerability(self, vulnerability):
        """ Add a given vulnerability to the systems in the admin's network. """
        for item in self.network.all_items:
            if item.__class__.__name__ in vulnerability.affects:
                _ = yield item.vulnerabilities.put(vulnerability)

    def remove_vulnerability(self, vulnerability, item):
        """ Remove a given vulnerability from the systems in the admin's network. """
        if vulnerability in item.vulnerabilities.items:
            _ = yield item.vulnerabilities.get(filter=lambda v: v == vulnerability)
        else:
            _ = yield self.timeout(0)

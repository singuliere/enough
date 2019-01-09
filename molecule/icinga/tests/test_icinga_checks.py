from tests.icinga_helper import IcingaHelper

testinfra_hosts = ['icinga-host']


class TestChecks(IcingaHelper):

    def test_disk(self):
        assert self.is_service_ok('monitoring-client-host!disk')
        assert self.is_service_ok('monitoring-client2-host!disk')

    def test_icinga_ntp_time(self):
        assert self.is_service_ok('monitoring-client-host!systemd-timesyncd is working')

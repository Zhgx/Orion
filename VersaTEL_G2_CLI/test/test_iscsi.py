from execute import iscsi
import subprocess


class TestDisk:

    def setup_class(self):
        self.disk = iscsi.Disk()

    def test_get_all_disk(self):
        assert self.disk.get_all_disk() != None

    def test_get_spe_disk(self):
        assert self.disk.get_spe_disk('res_a') != None

    def test_show_all_disk(self):
        assert self.disk.show_all_disk() == None

    def test_show_spe_disk(self):
        assert self.disk.show_spe_disk('res_a') == None


class TestHost:

    def setup_class(self):
        self.host = iscsi.Host()

    def test_create_host(self):
        assert self.host.create_host('test_host1', 'test_iqn') == True

    def test_get_all_host(self):
        assert self.host.get_all_host() != None

    def test_get_spe_host(self):
        assert self.host.get_spe_host('test_host1') != None

    def test_show_all_host(self):
        assert self.host.show_all_host() == None

    def test_show_spe_host(self):
        assert self.host.show_spe_host('test_host1') == None

    def test_delete_host(self):
        assert self.host.delete_host('test_host1') == True


class TestDiskGroup:

    def setup_class(self):
        self.diskg = iscsi.DiskGroup()
        subprocess.run('python vtel_client_main.py stor r c res_test -s 10m -a -num 1', shell=True)

    def teardown_class(self):
        subprocess.run('python vtel_client_main.py stor r d res_test -y', shell=True)


    def test_create_diskgroup(self):
        assert self.diskg.create_diskgroup('test_dg1', 'res_a') == True

    def test_get_all_diskgroup(self):
        assert self.diskg.get_all_diskgroup() != None

    def test_get_spe_diskgroup(self):
        assert self.diskg.get_spe_diskgroup('test_dg1') != None

    def test_show_all_diskgroup(self):
        assert self.diskg.show_all_diskgroup() == None

    def test_show_spe_diskgroup(self):
        assert self.diskg.show_spe_diskgroup('test_dg1') == None

    def test_delete_diskgroup(self):
        assert self.diskg.delete_diskgroup('test_dg1') == None


class TestHostGroup:

    def setup_class(self):
        self.hostg = iscsi.HostGroup()
        self.host = iscsi.Host()
        self.host.create_host('test_host1', 'test_iqn')

    def teardown_class(self):
        self.host.delete_host('test_host1')

    def test_create_hostgroup(self):
        assert self.hostg.create_hostgroup('test_hg1', 'test_host1') == True

    def test_get_all_hostgroup(self):
        assert self.hostg.get_all_hostgroup() != None

    def test_get_spe_hostgroup(self):
        assert self.hostg.get_spe_hostgroup('test_hg1') != None

    def test_show_all_hostgroup(self):
        assert self.hostg.show_all_hostgroup() == None

    def test_show_spe_hostgroup(self):
        assert self.hostg.show_spe_hostgroup('test_hg1') == None

    def test_delete_hostgroup(self):
        assert self.hostg.delete_hostgroup('test_hg1') == None


class TestMap:

    def setup_class(self):
        self.map = iscsi.Map()

    def teardown_class(self):
        pass

    def test_pre_check_create_map(self):
        pass

    def test_get_initiator(self):
        pass

    def test_get_target(self):
        pass

    def test_get_drbd_data(self):
        pass

    def test_create_map(self):
        pass

    def test_get_all_map(self):
        pass

    def test_get_spe_map(self):
        pass

    def test_show_all_map(self):
        pass
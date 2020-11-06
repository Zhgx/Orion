import iscsi_json


class TestJSON_OPERATION:

    def setup_class(self):
        self.js = iscsi_json.JsonOperation()

    def test_read_json(self):
        assert self.js.read_json() != None

    def test_add_data(self):
        data_host = self.js.add_data('Host', 'pytest_host', 'pytest_iqn')
        assert data_host['pytest_host'] == 'pytest_iqn'
        data_hg = self.js.add_data('HostGroup', 'pytest_hg', ['pytest_host1', 'pytest_host2'])
        assert data_hg['pytest_hg'] == ['pytest_host1', 'pytest_host2']
        data_dg = self.js.add_data('DiskGroup', 'pytest_dg', ['pytest_disk1', 'pytest_disk2'])
        assert data_dg['pytest_dg'] == ['pytest_disk1', 'pytest_disk2']
        data_map = self.js.add_data('Map', 'pytest_map', ['pytest_hg', 'pytest_dg'])
        assert data_map['pytest_map'] == ['pytest_hg', 'pytest_dg']

    def test_delete_data(self):
        data_map = self.js.delete_data('Map', 'pytest_map')
        assert 'pytest_map' not in data_map
        data = self.js.delete_data('DiskGroup', 'pytest_dg')
        assert 'pytest_dg' not in data
        data = self.js.delete_data('HostGroup', 'pytest_hg')
        assert 'pytest_hg' not in data
        data = self.js.delete_data('Host', 'pytest_host')
        assert 'pytest_host' not in data

    def test_get_data(self):
        self.js.add_data('Host', 'pytest_host', 'pytest_iqn')
        assert 'pytest_host' in self.js.get_data('Host')

    def test_check_key(self):
        result = self.js.check_key('Host', 'pytest_host')
        assert result['result'] == True
        result = self.js.check_key('Host', 'pytest_host_false')
        assert result['result'] == False

    def test_check_value(self):
        result = self.js.check_value('Host', 'pytest_iqn')
        assert result['result'] == True
        result = self.js.check_value('Host', 'pytest_iqn_false')
        assert result['result'] == False
        self.js.delete_data('Host', 'pytest_host')

    def test_update_data(self):
        data = self.js.update_data('Disk', {'pytest_disk':'pytest_path'})
        assert data == {'pytest_disk': 'pytest_path'}

    def test_update_crm_conf(self):
        resouce = [["thinlv_test",
                "iqn.2020-04.feixitek.com:versaplx00",
                "04",
                "/dev/drbd1004",
                "iqn123 ",
                "Started"]]
        vip = [["vip",
                "10.203.1.75",
                "24"]]
        target = [["t_test",
                "iqn.2020-04.feixitek.com:versaplx00",
                "10.203.1.75"]]
        assert self.js.update_crm_conf(resouce, vip, target) != None
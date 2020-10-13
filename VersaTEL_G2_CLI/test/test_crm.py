from execute import crm
import subprocess


def test_execute_crm_cmd():
    assert crm.execute_crm_cmd('pwd') != None


class TestCRMData:

    def setup_class(self):
        self.crmdata = crm.CRMData()

    def test_get_crm_conf(self):
        result = self.crmdata.get_crm_conf()
        assert 'primitive' in result

    def test_get_resource_data(self):
        assert self.crmdata.get_resource_data() != None

    def test_get_vip_data(self):
        assert self.crmdata.get_vip_data() != None

    def test_get_target_data(self):
        assert self.crmdata.get_target_data() != None

    def test_update_crm_conf(self):
        assert self.crmdata.update_crm_conf() == True


class TestCRMConfig:

    def setup_class(self):
        subprocess.run('python vtel_client_main.py stor r c res_test -s 10m -a -num 1', shell=True)
        subprocess.run('python vtel_client_main.py iscsi d s', shell=True)
        subprocess.run('python vtel_client_main.py iscsi dg c test_dg res_test', shell=True)
        subprocess.run('python vtel_client_main.py iscsi h c test_host iqn-123213-111', shell=True)
        subprocess.run('python vtel_client_main.py iscsi hg c test_hg test_host', shell=True)
        self.crmconfig = crm.CRMConfig()

    def teardown_class(self):
        subprocess.run('python vtel_client_main.py iscsi hg d test_hg', shell=True)
        subprocess.run('python vtel_client_main.py iscsi h d test_host', shell=True)
        subprocess.run('python vtel_client_main.py iscsi dg d test_dg', shell=True)
        subprocess.run('python vtel_client_main.py stor r d res_test -y', shell=True)

    def test_create_crm_res(self):
        assert self.crmconfig.create_crm_res('res_test', 'iqn.2020-04.feixitek.com:versaplx00', '05', '/dev/drbd1005', 'iqn-123213-111') == True

    def test_get_res_status(self):
        assert self.crmconfig.get_res_status('res_test') == 'Stopped'

    def test_checkout_status(self):
        assert self.crmconfig.checkout_status('res_test', 2, 'Stopped') == True

    def test_create_col(self):
        assert self.crmconfig.create_col('res_test', 't_test') == True

    def test_create_order(self):
        assert self.crmconfig.create_order('res_test', 't_test') == True

    def test_start_res(self):
        assert self.crmconfig.start_res('res_test') == True

    def test_stop_res(self):
        assert self.crmconfig.stop_res('res_test') == True

    def test_delete_crm_res(self):
        assert self.crmconfig.delete_crm_res('res_test') == True
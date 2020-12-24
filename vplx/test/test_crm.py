from execute import crm,iscsi
import subprocess
import time


def test_execute_crm_cmd():
    assert crm.execute_crm_cmd('pwd') != None


class TestCRMData:

    def setup_class(self):
        self.crmdata = crm.CRMData()

    def test_get_crm_conf(self):
        result = self.crmdata.get_crm_conf()
        assert 'primitive' in result

    def test_get_resource_data(self):
        assert self.crmdata.get_resource_data()

    def test_get_vip_data(self):
        assert self.crmdata.get_vip_data() != None

    def test_get_target_data(self):
        assert self.crmdata.get_target_data() != None

    def test_update_crm_conf(self):
        assert self.crmdata.update_crm_conf()


class TestCRMConfig:

    def setup_class(self):
        subprocess.run('python3 vtel_client_main.py stor r c res_test -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel_client_main.py iscsi d s', shell=True)
        subprocess.run('python3 vtel_client_main.py iscsi dg c test_dg res_test', shell=True)
        subprocess.run('python3 vtel_client_main.py iscsi h c test_host iqn.2020-11.com.example:pytest01', shell=True)
        subprocess.run('python3 vtel_client_main.py iscsi hg c test_hg test_host', shell=True)
        self.crmconfig = crm.CRMConfig()

    def teardown_class(self):
        subprocess.run('python3 vtel_client_main.py iscsi hg d test_hg', shell=True)
        subprocess.run('python3 vtel_client_main.py iscsi h d test_host', shell=True)
        subprocess.run('python3 vtel_client_main.py iscsi dg d test_dg', shell=True)
        subprocess.run('python3 vtel_client_main.py stor r d res_test -y', shell=True)

    def test_create_crm_res(self):
        disk = iscsi.Disk()
        disk_data = disk.get_all_disk()
        path = disk_data['res_test']
        id = int(path[-4:])-1000
        assert self.crmconfig.create_crm_res('res_test', 'iqn.2020-04.feixitek.com:versaplx00', id, path, 'iqn.2020-11.com.example:pytest01') == True

    def test_get_res_status(self):
        assert self.crmconfig.get_res_status('res_test') == False
        self.crmconfig.start_res('res_test')
        time.sleep(5)
        assert self.crmconfig.get_res_status('res_test') == True

    def test_checkout_status_start(self):
        assert self.crmconfig.checkout_status_start('res_test') == True

    def test_stop_res(self):
        assert self.crmconfig.stop_res('res_test') == True

    def test_checkout_status_stop(self):
        assert self.crmconfig.checkout_status_stop('res_test') == True

    def test_create_col(self):
        assert self.crmconfig.create_col('res_test', 't_test') == True

    def test_create_order(self):
        assert self.crmconfig.create_order('res_test', 't_test') == True

    def test_start_res(self):
        assert self.crmconfig.start_res('res_test') == True
        self.crmconfig.stop_res('res_test')

    def test_delete_conf_res(self):
        assert self.crmconfig.delete_conf_res('res_test') == True

    # def test_refresh(self):
    #     assert self.crmconfig.refresh() == True
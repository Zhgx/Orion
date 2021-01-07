import sys
from unittest.mock import patch

import consts
import log
import sundry
from execute import crm, iscsi
import subprocess
import time

from execute.crm import execute_crm_cmd


def test_module():
    sys.path.append('../')
    consts.init()

    # transaction_id = s.create_transaction_id()
    # logger = log.Log('test',transaction_id)
    # consts.set_glo_log(logger)
    # consts.set_glo_tsc_id(transaction_id)
    # # consts.set_glo_id(99)
    # # consts.set_glo_str('test')
    # consts.set_glo_rpl('no')
    transaction_id = sundry.create_transaction_id()
    logger = log.Log('test', transaction_id)
    consts.set_glo_log(logger)
    consts.set_glo_rpl('no')


def test_execute_crm_cmd():
    assert crm.execute_crm_cmd('pwd') is not None


class TestCRMData:

    def setup_class(self):
        self.crmdata = crm.CRMData()

    # result 类型 str ，命令行输出内容
    def test_get_crm_conf(self):
        result = self.crmdata.get_crm_conf()
        assert str == type(result)
        # assert 'res_a' in result
        assert 'primitive' in result

    # 函数名有改动/该函数被删除
    # def test_get_resource_data(self):
    #     assert self.crmdata.get_resource_data()
    #
    # def test_get_vip_data(self):
    #     assert self.crmdata.get_vip_data() is not None
    #
    # def test_get_target_data(self):
    #     assert self.crmdata.get_target_data() is not None
    #
    # # 无实际调用 iscsi_json 模块有其同名函数
    # def test_update_crm_conf(self):
    #     assert self.crmdata.update_crm_conf()


class TestCRMConfig:

    def setup_class(self):
        subprocess.run('python3 vtel.py stor r c res_test -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel.py iscsi d s', shell=True)
        subprocess.run('python3 vtel.py iscsi dg c test_dg res_test', shell=True)
        subprocess.run('python3 vtel.py iscsi h c test_host iqn.2020-11.com.example:pytest01', shell=True)
        subprocess.run('python3 vtel.py iscsi hg c test_hg test_host', shell=True)
        self.crmconfig = crm.CRMConfig()

    def teardown_class(self):
        subprocess.run('python3 vtel.py iscsi hg d test_hg -y', shell=True)
        subprocess.run('python3 vtel.py iscsi h d test_host -y', shell=True)
        subprocess.run('python3 vtel.py iscsi dg d test_dg -y', shell=True)
        try:
            execute_crm_cmd('crm res stop res_test')
            execute_crm_cmd('crm conf del res_test')
        except Exception:
            print(Exception)
        finally:
            subprocess.run('python3 vtel.py stor r d res_test -y', shell=True)
            subprocess.run('python3 vtel.py iscsi d s', shell=True)

    def test_create_crm_res(self):
        disk = iscsi.Disk()
        disk_data = disk.get_all_disk()
        path = disk_data['res_test']
        id = int(path[-4:]) - 1000
        assert self.crmconfig.create_crm_res('res_test', 'iqn.2020-04.feixitek.com:versaplx00', id, path,
                                             'iqn.2020-11.com.example:pytest01') is True

    # 函数已删除
    # def test_get_res_status(self):
    #     assert self.crmconfig.get_res_status('res_test') is False
    #     self.crmconfig.start_res('res_test')
    #     time.sleep(5)
    #     assert self.crmconfig.get_res_status('res_test') is True

    # 函数已删除
    # def test_checkout_status_start(self):
    #     assert self.crmconfig.checkout_status_start('res_test') is True

    def test_stop_res(self):
        assert self.crmconfig.stop_res('res_test') is True

    # 函数已删除
    # def test_checkout_status_stop(self):
    #     assert self.crmconfig.checkout_status_stop('res_test') is True

    def test_create_col(self):
        assert self.crmconfig.create_col('res_test', 't_test') is True

    def test_create_order(self):
        assert self.crmconfig.create_order('res_test', 't_test') is True

    def test_start_res(self):
        assert self.crmconfig.start_res('res_test') is True
        self.crmconfig.stop_res('res_test')

    # 函数已删除
    # def test_delete_conf_res(self):
    #     assert self.crmconfig.delete_conf_res('res_test') is True

    # ------------- add ----------------   2020.12.28

    def test_change_initiator(self):
        assert self.crmconfig.change_initiator('res_test', ['iqn.2020-11.com.example:pytest01'])

    def test_delete_res(self):
        assert self.crmconfig.delete_res('res_test', 'iSCSILogicalUnit')
        # 删除一个不存在资源
        with patch('builtins.print') as terminal_print:
            self.crmconfig.delete_res('res_test0', 'iSCSILogicalUnit')
            terminal_print.assert_called_with('Delete res_test0 fail')


    # 有调用关系，不能单独测，create_res调用create_crm_res再调用create_set然后在调用create_col和create_order
    # 需要先创建crm_res,create_set方法主要是创建colocation和order
    def test_create_set(self):
        disk = iscsi.Disk()
        disk_data = disk.get_all_disk()
        path = disk_data['res_test']
        lunid = int(path[-4:]) - 1000
        self.crmconfig.create_crm_res('res_test', 'iqn.2020-04.feixitek.com:versaplx00', lunid, path,
                                      'iqn.2020-11.com.example:pytest01')
        assert self.crmconfig.create_set('res_test', 't_test')
        self.crmconfig.delete_res('res_test', 'iSCSILogicalUnit')
        # 如果 crm_res 不存在该函数调用失败
        with patch('builtins.print') as terminal_print:
            self.crmconfig.create_set('res_test', 't_test')
            terminal_print.assert_called_with('create colocation fail')

    # 函数未被调用
    # def test_refresh(self):
    #     assert self.crmconfig.refresh() is True

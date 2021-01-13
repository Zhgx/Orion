import sys
from collections import Counter
from unittest.mock import patch

import pytest

import consts
import log
import sundry
from execute import crm, iscsi
import subprocess
import time

from execute.crm import execute_crm_cmd


def test_module():
    print('test_module')
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

    @pytest.mark.portal
    def test_get_vip(self):
        """获取 crm 全部 vip 信息"""
        print('get_vip', self.crmdata.get_vip())
        # assert self.crmdata.get_vip() == {'portal_test_4': {'ip': '10.203.1.201', 'netmask': '24'},
        #                                   'vip': {'ip': '10.203.1.75', 'netmask': '24'},
        #                                   'vip_test2': {'ip': '10.203.1.206', 'netmask': '24'}}
        assert self.crmdata.get_vip() is not None

    @pytest.mark.portal
    def test_get_portblock(self):
        """获取 crm 全部 portblock 信息"""
        print('get_portblock', self.crmdata.get_portblock())
        # assert self.crmdata.get_portblock() == {
        #     'p_iscsi_portblock_off': {'ip': '10.203.1.75', 'port': '3260', 'type': 'unblock'},
        #     'p_iscsi_portblock_on': {'ip': '10.203.1.75', 'port': '3260', 'type': 'block'},
        #     'portal_test_4_prtblk_off': {'ip': '10.203.1.201', 'port': '3260', 'type': 'unblock'},
        #     'portal_test_4_prtblk_on': {'ip': '10.203.1.201', 'port': '3260', 'type': 'block'},
        #     'vip_test2_prtblk_off': {'ip': '10.203.1.200', 'port': '3260', 'type': 'unblock'},
        #     'vip_test2_prtblk_on': {'ip': '10.203.1.200', 'port': '3260', 'type': 'block'}}
        assert self.crmdata.get_portblock() is not None

    @pytest.mark.portal
    def test_get_target(self):
        """获取 crm 全部 target 信息"""
        print('get_target', self.crmdata.get_target())
        # assert self.crmdata.get_target() == {
        #     't_test': {'target_iqn': 'iqn.2020-04.feixitek.com:versaplx00', 'ip': '10.203.1.75', 'port': '3260'}}
        assert self.crmdata.get_target() is not None

    @pytest.mark.portal
    def test_get_portal_data(self):
        """获取 crm 全部 portal data 信息"""
        print('get_portal_data', self.crmdata.get_portal_data(self.crmdata.get_vip(), self.crmdata.get_portblock(),
                                           self.crmdata.get_target()))
        # assert self.crmdata.get_portal_data(self.crmdata.get_vip(), self.crmdata.get_portblock(),
        #                                     self.crmdata.get_target()) == {
        #            'portal_test_4': {'ip': '10.203.1.201', 'port': '3260', 'netmask': '24', 'target': []},
        #            'vip': {'ip': '10.203.1.75', 'port': '3260', 'netmask': '24', 'target': ['t_test']},
        #            'vip_test2': {'ip': '10.203.1.200', 'port': '3260', 'netmask': '24', 'target': []}}
        assert self.crmdata.get_portal_data(self.crmdata.get_vip(), self.crmdata.get_portblock(),
                                            self.crmdata.get_target()) is not None

    @pytest.mark.portal
    def test_check_portal_component(self):
        """对目前环境的portal组件(ipaddr,portblock）的检查，测试用例包括：已存在的ipaddr没有对应的portblock抛出异常/存在单独的portblock抛出异常/不存在异常情况检查通过"""
        # 1.不存在单独的 portblock
        # 2.已存在的ipaddr，必须有对应的portblock组（block，unblock）
        # 尝试单独创建 ipaddr
        # 这些portal无法正常使用，请进行处理
        subprocess.run('crm cof primitive vip_pytest03 IPaddr2 params ip=10.203.1.202 cidr_netmask=24 -y', shell=True)
        # 需要重新实例化，不然单独创建 IPaddr2 没法在初始化的对象中读取
        crmdata = crm.CRMData()
        with pytest.raises(SystemExit) as exsinfo:
            crmdata.check_portal_component(crmdata.get_vip(), crmdata.get_portblock())
        assert exsinfo.type == SystemExit
        subprocess.run('crm res stop vip_pytest03', shell=True)
        subprocess.run('crm conf del vip_pytest03', shell=True)
        # 重新初始化对象
        subprocess.run('crm cof primitive vip_pytest03_prtblk_on portblock params ip=10.203.1.202 portno=24 protocol=tcp action=block op monitor timeout=20 interval=20 -y', shell=True)
        crmdata = crm.CRMData()
        with pytest.raises(SystemExit) as exsinfo:
            crmdata.check_portal_component(crmdata.get_vip(), crmdata.get_portblock())
        assert exsinfo.type == SystemExit
        subprocess.run('crm res stop vip_pytest03_prtblk_on', shell=True)
        subprocess.run('crm conf del vip_pytest03_prtblk_on', shell=True)
        # 重新初始化对象
        crmdata = crm.CRMData()
        assert crmdata.check_portal_component(crmdata.get_vip(), crmdata.get_portblock()) is None

    def test_check_env_sync(self):
        assert self.crmdata.check_env_sync(self.crmdata.get_vip(), self.crmdata.get_portblock(),
                                           self.crmdata.get_target()) is None

    # check 函数调用 check_portal_component 和 check_env_sync 函数不作用例分析
    def test_check(self):
        """check 函数调用 check_portal_component 和 check_env_sync 函数不作用例分析"""
        assert self.crmdata.check() is None


class TestCRMConfig:

    # def setup_class(self):
    #     self.crmconfig = crm.CRMConfig()

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
        # attention
        disk_data = disk.show('res_test')
        path = disk_data[0][1]
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

    # # 函数已删除
    # # def test_checkout_status_stop(self):
    # #     assert self.crmconfig.checkout_status_stop('res_test') is True
    #
    # def test_create_col(self):
    #     assert self.crmconfig.create_col('res_test', 't_test') is True
    #
    # def test_create_order(self):
    #     assert self.crmconfig.create_order('res_test', 't_test') is True

    def test_start_res(self):
        assert self.crmconfig.start_res('res_test') is True
        self.crmconfig.stop_res('res_test')

    # 函数已删除
    # def test_delete_conf_res(self):
    #     assert self.crmconfig.delete_conf_res('res_test') is True

    # ------------- add ----------------   2020.12.28

    # def test_change_initiator(self):
    #     assert self.crmconfig.change_initiator('res_test', ['iqn.2020-11.com.example:pytest01'])

    def test_delete_res(self):
        assert self.crmconfig.delete_res('res_test', 'iSCSILogicalUnit')
        # 删除一个不存在资源
        with patch('builtins.print') as terminal_print:
            self.crmconfig.delete_res('res_test0', 'iSCSILogicalUnit')
            terminal_print.assert_called_with('Delete res_test0 fail')

    def test_checkout_status(self):
        assert self.crmconfig.checkout_status('', 'iSCSILogicalUnit', 'STARTED') is None

    def test_execute_delete(self):
        # 删除不存在资源
        assert not self.crmconfig.execute_delete('res_test0')

    def test_refresh(self):
        # 暂未调用，单独使用刷新命令result['sts'] == 0 if 条件不通过
        pass

    # 函数已删除
    # 有调用关系，不能单独测，create_res调用create_crm_res再调用create_set然后在调用create_col和create_order
    # 需要先创建crm_res,create_set方法主要是创建colocation和order
    # def test_create_set(self):
    #     disk = iscsi.Disk()
    #     disk_data = disk.get_all_disk()
    #     path = disk_data['res_test']
    #     lunid = int(path[-4:]) - 1000
    #     self.crmconfig.create_crm_res('res_test', 'iqn.2020-04.feixitek.com:versaplx00', lunid, path,
    #                                   'iqn.2020-11.com.example:pytest01')
    #     assert self.crmconfig.create_set('res_test', 't_test')
    #     self.crmconfig.delete_res('res_test', 'iSCSILogicalUnit')
    #     # 如果 crm_res 不存在该函数调用失败
    #     with patch('builtins.print') as terminal_print:
    #         self.crmconfig.create_set('res_test', 't_test')
    #         terminal_print.assert_called_with('create colocation fail')

    # 函数未被调用
    # def test_refresh(self):
    #     assert self.crmconfig.refresh() is True
    @pytest.mark.portal
    def test_get_failed_actions(self):
        """提取 vip 错误信息，测试用例包括：该vip有错误信息/该vip没有错误信息"""
        subprocess.run('crm cof primitive vip_pytest10 IPaddr2 params ip=10.203.1.209 cidr_netmask=50', shell=True)
        crmconfig = crm.CRMConfig()
        assert crmconfig.get_failed_actions('vip_pytest10') == 0
        # 没有报错信息，return None
        assert crmconfig.get_failed_actions('abd') is None
        subprocess.run('crm conf del vip_pytest10', shell=True)

    @pytest.mark.portal
    def test_get_crm_res_status(self):
        """获取crm res的状态，测试用例包括：获取状态成功/资源类型输入错误/资源名字与类型不对应"""
        assert self.crmconfig.get_crm_res_status('p_iscsi_portblock_off', 'IPaddr2') is None
        assert self.crmconfig.get_crm_res_status('vip', 'IPaddr2')
        with pytest.raises(ValueError) as exsinfo:
            self.crmconfig.get_crm_res_status('vip', 'IPaddr1')
        assert exsinfo.type == ValueError


# class TestRollback:
#
#     def setup_class(self):
#         self.rb = crm.RollBack()
#
#     def test_rollback(self):
#         # rollback 调用 rb_ipaddr2() rb.rb_block() rb_target()
#         assert self.rb.rollback() is None
#
#     def test_rb_ipaddr2(self):
#         assert self.rb.rb_ipaddr2() is None
#
#     def test_rb_block(self):
#         assert self.rb.rb_block() is None
#
#     def test_rb_target(self):
#         assert self.rb.rb_target() is None

@pytest.mark.portal
class TestIPaddr2:

    def setup_class(self):
        self.ipaddr2 = crm.IPaddr2()

    def test_create(self):
        """创建IPaddr2，测试用例包括：创建IPaddr2成功/IPaddr2已存在创建失败"""
        # 端口 与ip 前面函数已校验
        assert self.ipaddr2.create.__wrapped__(self, 'vip_pytest03', '10.203.1.202', '24')
        # with pytest.raises(consts.CmdError) as exsinfo:
        #     self.ipaddr2.create.__wrapped__(self, 'vip_pytest04', '10.203.1....202', '24')
        # assert exsinfo.type == consts.CmdError
        # with pytest.raises(consts.CmdError) as exsinfo:
        #     self.ipaddr2.create.__wrapped__(self, 'vip_pytest05', '10.203.1.206', '40')
        # assert exsinfo.type == consts.CmdError
        with pytest.raises(consts.CmdError) as exsinfo:
            self.ipaddr2.create.__wrapped__(self, 'vip_pytest03', '10.203.1.202', '40')
        assert exsinfo.type == consts.CmdError

    def test_modify(self):
        """修改IPaddr2，测试用例包括：修改IPaddr2成功/IPaddr2不存在修改失败"""
        assert self.ipaddr2.modify.__wrapped__(self, 'vip_pytest03', '10.203.1.203')
        # ip格式问题前面函数已校验
        # with pytest.raises(consts.CmdError) as exsinfo:
        #     self.ipaddr2.modify.__wrapped__(self, 'vip_pytest03', '10.203.1.202....')
        # assert exsinfo.type == consts.CmdError
        with pytest.raises(consts.CmdError) as exsinfo:
            self.ipaddr2.modify.__wrapped__(self, 'vip_pytest05', '10.203.1.202')
        assert exsinfo.type == consts.CmdError

    def test_delete(self):
        """删除IPaddr2，测试用例包括：删除IPaddr2成功/IPaddr2不存在删除失败"""
        assert self.ipaddr2.delete.__wrapped__(self, 'vip_pytest03')
        with pytest.raises(consts.CmdError) as exsinfo:
            self.ipaddr2.delete.__wrapped__(self, 'vip_pytest05')
        assert exsinfo.type == consts.CmdError


@pytest.mark.portal
class TestPortBlockGroup:

    def setup_class(self):
        self.pbg = crm.PortBlockGroup()

    def test_create(self):
        """创建PortBlockGroup，测试用例包括：创建类型非block/unblock创建失败/创建成功/已存在创建失败"""
        with pytest.raises(TypeError) as exsinfo:
            self.pbg.create.__wrapped__(self, 'vip_pytest03_prtblk_on', '10.203.1.202', '24', None)
        assert exsinfo.type == TypeError

        assert self.pbg.create.__wrapped__(self, 'vip_pytest03_prtblk_on', '10.203.1.202', '24', 'block')
        assert self.pbg.create.__wrapped__(self, 'vip_pytest03_prtblk_off', '10.203.1.202', '24', 'unblock')

        with pytest.raises(consts.CmdError) as exsinfo:
            self.pbg.create.__wrapped__(self, 'vip_pytest03_prtblk_off', '10.203.1.202', '24', 'unblock')
        assert exsinfo.type == consts.CmdError

    def test_modify(self):
        """修改PortBlockGroup，测试用例包括：修改成功/不存在修改失败"""
        assert self.pbg.modify.__wrapped__(self, 'vip_pytest03_prtblk_on', '10.203.1.203', '24')
        assert self.pbg.modify.__wrapped__(self, 'vip_pytest03_prtblk_off', '10.203.1.203', '24')

    def test_delete(self):
        """删除PortBlockGroup，测试用例包括：删除成功/不存在删除失败"""
        assert self.pbg.delete.__wrapped__(self, 'vip_pytest03_prtblk_on')
        assert self.pbg.delete.__wrapped__(self, 'vip_pytest03_prtblk_off')


class TestColocation:
    def test_create(self):
        """创建Colocation，测试用例包括：创建Colocation成功/使用不存在资源创建Colocation"""
        subprocess.run('python3 vtel.py stor r c res_test -s 10m -a -num 1', shell=True)
        disk = iscsi.Disk()
        disk_data = disk.show('res_test')
        path = disk_data[0][1]
        lunid = int(path[-4:]) - 1000
        # 要先创建 resource 才可以创建 colocation
        colocation = crm.Colocation()
        iscsilu = crm.ISCSILogicalUnit()
        iscsilu.create('res_test', 'iqn.2020-04.feixitek.com:versaplx00', lunid, path,
                       'iqn.2020-11.com.example:pytest01')
        # 创建成功
        assert colocation.create('col_res_test', 'res_test', iscsilu.target_name)
        # 数据清除
        subprocess.run('crm res stop res_test', shell=True)
        subprocess.run('crm conf del res_test', shell=True)
        subprocess.run('python3 vtel.py stor r d res_test -y', shell=True)
        subprocess.run('python3 vtel.py iscsi d s', shell=True)
        # resource 不存在
        with pytest.raises(consts.CmdError) as exsinfo:
            colocation.create('col_res_test0', 'res_test0', iscsilu.target_name)
        assert exsinfo.type == consts.CmdError


class TestOrder:
    def test_create(self):
        """创建Order，测试用例包括：创建Colocation成功/使用不存在资源创建Colocation"""
        subprocess.run('python3 vtel.py stor r c res_test -s 10m -a -num 1', shell=True)
        disk = iscsi.Disk()
        disk_data = disk.show('res_test')
        path = disk_data[0][1]
        lunid = int(path[-4:]) - 1000
        iscsilu = crm.ISCSILogicalUnit()
        iscsilu.create('res_test', 'iqn.2020-04.feixitek.com:versaplx00', lunid, path,
                       'iqn.2020-11.com.example:pytest01')
        # 要先创建 resource 才可以创建 colocation
        order = crm.Order()
        # 创建成功
        assert order.create('or_res_test', iscsilu.target_name, 'res_test')
        # 数据清除
        subprocess.run('crm res stop res_test', shell=True)
        subprocess.run('crm conf del res_test', shell=True)
        subprocess.run('python3 vtel.py stor r d res_test -y', shell=True)
        subprocess.run('python3 vtel.py iscsi d s', shell=True)
        # resource和colocation不存在
        with pytest.raises(consts.CmdError) as exsinfo:
            assert order.create('or_res_test0', iscsilu.target_name, 'res_test0')
        assert exsinfo.type == consts.CmdError


class TestISCSITarget:
    def test_modify(self):
        """修改ISCSITarget，当修改已配置target的portal信息时，对应的target也会修改,测试用例包括：修改target成功/target不存在修改失败"""
        iscsi_target = iscsi.ISCSITarget()
        assert iscsi_target.modify.__wrapped__(self, 't_test', '10.203.1.75', '3260')
        with pytest.raises(consts.CmdError) as exsinfo:
            assert iscsi_target.modify.__wrapped__(self, 't_test0', '10.203.1.75', '3260')
        assert exsinfo.type == consts.CmdError


class TestISCSILogicalUnit:

    def setup_class(self):
        subprocess.run('python3 vtel.py stor r c res_test -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel.py iscsi d s', shell=True)
        subprocess.run('python3 vtel.py iscsi h c test_host1 iqn.2020-04.feixitek.com:pytest01', shell=True)
        subprocess.run('python3 vtel.py iscsi h c test_host2 iqn.2020-04.feixitek.com:pytest002', shell=True)

        self.iscsilu = crm.ISCSILogicalUnit()

    def teardown_class(self):
        print('teardown')
        subprocess.run('python3 vtel.py iscsi h d test_host1 -y', shell=True)
        subprocess.run('python3 vtel.py iscsi h d test_host2 -y', shell=True)
        subprocess.run('crm res stop res_test', shell=True)
        subprocess.run('crm conf del res_test', shell=True)
        subprocess.run('python3 vtel.py stor r d res_test -y', shell=True)
        subprocess.run('python3 vtel.py iscsi d s', shell=True)

    def test_get_target(self):
        """获取crm target 信息"""
        assert self.iscsilu.get_target() == ('t_test', 'iqn.2020-04.feixitek.com:versaplx00')

    def test_create(self):
        """创建ISCSILogicalUnit"""
        disk = iscsi.Disk()
        disk_data = disk.show('res_test')
        path = disk_data[0][1]
        lunid = int(path[-4:]) - 1000
        iscsilu = crm.ISCSILogicalUnit()
        assert iscsilu.create('res_test', 'iqn.2020-04.feixitek.com:versaplx00', lunid, path,
                              'iqn.2020-11.com.example:pytest01')
        # ISCSILogicalUnit 已存在
        with pytest.raises(consts.CmdError) as exsinfo:
            iscsilu.create('res_test', 'iqn.2020-04.feixitek.com:versaplx00', lunid, path,
                           'iqn.2020-11.com.example:pytest01')
        assert exsinfo.type == consts.CmdError
        # 数据清洗
        subprocess.run('crm res stop res_test', shell=True)
        subprocess.run('crm conf del res_test', shell=True)

    def test_create_mapping(self):
        """创建mapping"""
        assert self.iscsilu.create_mapping('res_test', ['iqn.2020-04.feixitek.com:pytest01'])

    def test_modify(self):
        """修改ISCSILogicalUnit映射iqn"""
        assert self.iscsilu.modify('res_test',
                                   ['iqn.2020-04.feixitek.com:pytest01', 'iqn.2020-04.feixitek.com:pytest002'])

    def test_delete(self):
        """删除ISCSILogicalUnit"""
        assert self.iscsilu.delete('res_test')
        # 删除不存在
        with pytest.raises(consts.CmdError) as exsinfo:
            self.iscsilu.delete('res_test')
        assert exsinfo.type == consts.CmdError

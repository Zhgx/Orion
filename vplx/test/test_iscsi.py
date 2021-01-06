import os
import sys
import time
from unittest.mock import patch

import pytest

import iscsi_json
from execute import iscsi
import subprocess
from execute.crm import execute_crm_cmd


class TestDisk:

    def setup_class(self):
        subprocess.run('python3 vtel.py stor r c res_test1 -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel.py stor r c res_test2 -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel.py iscsi d s', shell=True)
        self.disk = iscsi.Disk()

    def teardown_class(self):
        subprocess.run('python3 vtel.py stor r d res_test1 -y', shell=True)
        subprocess.run('python3 vtel.py stor r d res_test2 -y', shell=True)
        subprocess.run('python3 vtel.py stor r s', shell=True)
        # json 文件不能及时更新,调用方法进行手动更新该对象（不调用的话 json 文件的disk 还是在）
        self.disk.show_all_disk()

    # 获取 linstor res
    def test_get_all_disk(self):
        assert 'res_test1' in self.disk.get_all_disk()
        assert 'res_test2' in self.disk.get_all_disk()

    # 这个函数应该明确获得指定disk,如果没有获得指定disk则return None
    def test_get_spe_disk(self):
        assert self.disk.get_spe_disk('res_test1')
        assert self.disk.get_spe_disk('res_test') is None

    # 该函数没有返回值，调用了本模块get_all_disk()和sundry的show_iscsi_data()
    def test_show_all_disk(self):
        assert self.disk.show_all_disk() is None

    # 该函数没有返回值，调用了本模块get_spe_disk()和sundry的show_iscsi_data()
    def test_show_spe_disk(self):
        assert self.disk.show_spe_disk('res_test') is None


class TestHost:

    def setup_class(self):
        print('setup_class')
        subprocess.run('python3 vtel.py iscsi h c test_host iqn.2020-04.feixitek.com:pytest0001', shell=True)
        subprocess.run('python3 vtel.py iscsi h c test_host_hg iqn.2020-04.feixitek.com:pytest0991', shell=True)
        subprocess.run('python3 vtel.py iscsi h s', shell=True)
        subprocess.run('python3 vtel.py iscsi hg c test_hg test_host_hg', shell=True)
        subprocess.run('python3 vtel.py iscsi h s', shell=True)
        self.host = iscsi.Host()

    def teardown_class(self):
        print('teardown_class')

    # 已存在返回 None ，新建成功返回 True
    def test_create_host(self):
        # 存在
        with patch('builtins.print') as terminal_print:
            self.host.create_host('test_host', 'iqn.2020-04.feixitek.com:pytest001')
            terminal_print.assert_called_with('Fail! The Host test_host already existed.')
        # 不存在，但iqn 格式不正确（要未新建过的host名才会判断iqn格式）
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.host.create_host('test_host3', 'iqn1')
                terminal_print.assert_called_with('The format of IQN is wrong. Please confirm and fill in again.')
        assert exsinfo.type == SystemExit
        # 新建成功
        assert self.host.create_host('test_host1', 'iqn.2020-04.feixitek.com:pytest01')

    # 已存在返回该host ，不存在返回None
    def test_get_spe_host(self):
        assert self.host.get_spe_host('test_host')
        assert not self.host.get_spe_host('test_host2')

    # 该函数没有返回值，调用了本模块get_all_host()和sundry的show_iscsi_data()
    def test_show_all_host(self):
        # 等价于 assert not None
        assert not self.host.show_all_host()
        # self.hostgroup.create_hostgroup('test_dg', ['test_host_dg'])
        # self.hostgroup.show_all_hostgroup()

    # 该函数没有返回值，调用了本模块get_spe_host()和sundry的show_iscsi_data()
    def test_show_spe_host(self):
        # 等价于 assert not None
        assert not self.host.show_spe_host('test_host_hg')

    def test_modify_host(self):
        # 不存在 host
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.host.modify_host('test_hostABC', 'iqn.2020-04.feixitek.com:pytest0999')
                terminal_print.assert_called_with('不存在这个host可以去进行修改')
        assert exsinfo.type == SystemExit
        #

    # 1.先检查host 是否存在，不存在输出提示语句 2.再判断该host 是否已经配置在HostGroup里，已配置返回输出提示语句
    # 3.不满足前两个返回条件，删除后返回True
    def test_delete_host(self):
        # 不存在
        print('delete_host test_funtion')
        with patch('builtins.print') as terminal_print:
            self.host.delete_host('test_hostABC')
            terminal_print.assert_called_with('Fail! Can\'t find test_hostABC')
        # 删除已存在而且没有配置在HostGroup中的host
        assert self.host.delete_host('test_host1')
        # 已配置用例有待添加
        with patch('builtins.print') as terminal_print:
            self.host.delete_host('test_host_hg')
            terminal_print.assert_called_with('Fail! The host in ... hostgroup.Please delete the hostgroup first')
        # self.hostgroup.delete_hostgroup('hg1')

    # 返回所有host，如果host为空，返回{},否则返回host字典
    def test_get_all_host(self):
        self.hostgroup = iscsi.HostGroup()
        #
        # self.host.delete_host('test_host_hg')
        # host 不为空
        assert self.host.get_all_host()
        # host 为空
        print('delete diskgroup：')
        self.hostgroup.delete_hostgroup('test_hg')
        print('first delete host：')
        self.host.delete_host('test_host')
        print('seconde delete host：')
        self.host.delete_host('test_host_hg')
        self.host.show_all_host()
        self.host.get_spe_host('test_host_hg')
        assert self.host.get_all_host() == {}

    # -------------  add -------------- 2020.12.28
    def test_check_iqn(self):
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.host.check_iqn('iqn1')
                terminal_print.assert_called_with('The format of IQN is wrong. Please confirm and fill in again.')
        assert exsinfo.type == SystemExit
        assert not self.host.check_iqn('iqn.2020-04.feixitek.com:pytest01')


class TestDiskGroup:

    def setup_class(self):
        subprocess.run('python3 vtel.py stor r c res_test -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel.py stor r c res_a -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel.py iscsi d s', shell=True)
        subprocess.run('python3 vtel.py iscsi h c test_host iqn.2020-04.feixitek.com:pytest0999', shell=True)
        # subprocess.run('python3 vtel.py iscsi d s', shell=True)
        subprocess.run('python3 vtel.py iscsi dg c test_dg res_test', shell=True)
        subprocess.run('python3 vtel.py iscsi hg c test_hg test_host', shell=True)
        # 创建 Map
        subprocess.run('python3 vtel.py iscsi m c map1 -dg test_dg -hg test_hg', shell=True)
        subprocess.run('python3 vtel.py iscsi m s', shell=True)

        self.diskg = iscsi.DiskGroup()
        self.map = iscsi.Map()

    def teardown_class(self):
        print('teardown')
        try:
            execute_crm_cmd('crm res stop res_test')
            execute_crm_cmd('crm conf del res_test')
            execute_crm_cmd('crm res stop res_a')
            execute_crm_cmd('crm conf del res_a')
        except Exception:
            print(Exception)
        finally:
            subprocess.run('python3 vtel.py stor r d res_test -y', shell=True)
            subprocess.run('python3 vtel.py stor r d res_a -y', shell=True)
        subprocess.run('python3 vtel.py iscsi d s', shell=True)
        subprocess.run('python3 vtel.py iscsi hg d test_hg -y', shell=True)
        subprocess.run('python3 vtel.py iscsi h d test_host -y', shell=True)

        # path = '../vplx/map_config.json'
        # os.remove(path)

    # 1.判断 DiskGroup 是否存在，存在返回 None 2.遍历 disk 列表，若发现 disk 不存在返回 None 3.创建成功返回 True
    def test_create_diskgroup(self):
        # DiskGroup 已存在
        assert not self.diskg.create_diskgroup('test_dg', ['res_test'])
        with patch('builtins.print') as terminal_print:
            self.diskg.create_diskgroup('test_dg', ['res_test'])
            terminal_print.assert_called_with('Fail! The Disk Group test_dg already existed.')
        # disk 不存在
        with patch('builtins.print') as terminal_print:
            self.diskg.create_diskgroup('test_dg1', ['res_test', 'res_test0'])
            terminal_print.assert_called_with('Fail! Can\'t find res_test0.Please give the true name.')
        # 创建成功的测试用例
        assert self.diskg.create_diskgroup('test_dg1', ['res_test'])

    # 返回指定 DiskGroup ，如果为 DiskGroup 不存在，返回 None,否则返回该 DiskGroup
    def test_get_spe_diskgroup(self):
        # DiskGroup 不存在测试用例
        assert not self.diskg.get_spe_diskgroup('test_dg2')
        # DiskGroup 存在测试用例
        assert self.diskg.get_spe_diskgroup('test_dg1')

    # 该函数没有返回值，调用了本模块get_all_diskgroup()和sundry的show_iscsi_data()
    def test_show_all_diskgroup(self):
        assert self.diskg.show_all_diskgroup() is None

    # 该函数没有返回值，调用了本模块get_spe_diskgroup()和sundry的show_iscsi_data()
    def test_show_spe_diskgroup(self):
        assert self.diskg.show_spe_diskgroup('test_dg1') is None

    # 1.先检查 HostGroup 是否存在，不存在返回 None 2.再判断 HostGroup 是否已经配置在 Map里，已配置返回None 3.不满足前两个返回条件，删除后依然返回None
    # 这个方法无返回值
    def test_delete_diskgroup(self):
        with patch('builtins.print') as terminal_print:
            self.diskg.delete_diskgroup('test_dg2')
            terminal_print.assert_called_with('Fail! Can\'t find test_dg2')
        # 保留测试用例，该分支有bug
        with patch('builtins.print') as terminal_print:
            self.map.show_spe_map('map1')
            self.diskg.delete_diskgroup('test_dg')
            terminal_print.assert_called_with('Fail! The diskgroup already map,Please delete the map')
        with patch('builtins.print') as terminal_print:
            self.diskg.delete_diskgroup('test_dg1')
            terminal_print.assert_called_with('Delete success!')

    # -----------   add  -----------------  2020.12.28
    def test_add_disk(self):
        # 新增成功
        assert not self.diskg.add_disk('test_dg', ['res_a'])
        # 不存在
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.diskg.add_disk('test_dg2', ['res_a'])
                terminal_print.assert_called_with('不存在test_dg2可以去进行修改')
        assert exsinfo.type == SystemExit
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.diskg.add_disk('test_dg', ['res_test'])
                terminal_print.assert_called_with('res_test已存在test_dg中')
        assert exsinfo.type == SystemExit
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.diskg.add_disk('test_dg', ['res_O'])
                terminal_print.assert_called_with('json文件中不存在res_O，无法进行添加')
        assert exsinfo.type == SystemExit

    def test_remove_disk(self):
        # 移除成功
        print('移除前')
        self.diskg.show_spe_diskgroup('test_dg')
        assert not self.diskg.remove_disk('test_dg', ['res_a'])
        # 移除失败
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.diskg.remove_disk('test_dg2', ['res_a'])
                terminal_print.assert_called_with('不存在test_dg2可以去进行修改')
        assert exsinfo.type == SystemExit
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.diskg.remove_disk('test_dg', ['res_O'])
                terminal_print.assert_called_with('test_dg中不存在成员res_O，无法进行移除')
        assert exsinfo.type == SystemExit
        # 只有一个资源移除后是否会删掉该dg , 会移除该 hg 和 所配置该 hg 的map
        with patch('builtins.print') as terminal_print:
            self.diskg.remove_disk('test_dg', ['res_test'])
            terminal_print.assert_called_with('相关的map已经修改/删除')
        # self.map.delete_map('map1')
        # self.diskg.delete_diskgroup('test_dg')

    # 返回所有 DiskGroup，如果为 DiskGroup 空，返回{},否则返回 DiskGroup 非空字典
    def test_get_all_diskgroup(self):
        # DiskGroup 不为空
        assert self.diskg.create_diskgroup('test_dg1', ['res_test'])
        print('show all diskgroup')
        self.diskg.show_all_diskgroup()
        assert self.diskg.get_all_diskgroup()
        # DiskGroup 为空
        # self.map.delete_map('map1')
        self.diskg.delete_diskgroup('test_dg1')
        assert self.diskg.get_all_diskgroup() == {}


class TestHostGroup:

    def setup_class(self):
        self.host = iscsi.Host()
        self.host.create_host('test_host1', 'iqn.2020-04.feixitek.com:pytest01')
        self.host.create_host('test_host2', 'iqn.2020-04.feixitek.com:pytest002')
        subprocess.run('python3 vtel.py stor r c res_test -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel.py iscsi d s', shell=True)
        subprocess.run('python3 vtel.py iscsi dg c test_dg res_test', shell=True)
        subprocess.run('python3 vtel.py iscsi hg c test_hg test_host1', shell=True)
        # 创建 Map
        subprocess.run('python3 vtel.py iscsi m c map1 -dg test_dg -hg test_hg', shell=True)
        subprocess.run('python3 vtel.py iscsi m s', shell=True)

        self.hostg = iscsi.HostGroup()
        self.map = iscsi.Map()

    def teardown_class(self):
        try:
            execute_crm_cmd('crm res stop res_test')
            execute_crm_cmd('crm conf del res_test')
        except Exception:
            print(Exception)
        finally:
            subprocess.run('python3 vtel.py stor r d res_test -y', shell=True)
            subprocess.run('python3 vtel.py iscsi d s', shell=True)
        subprocess.run('python3 vtel.py iscsi h d test_host1 -y', shell=True)
        subprocess.run('python3 vtel.py iscsi h d test_host2 -y', shell=True)
        subprocess.run('python3 vtel.py iscsi d s', shell=True)
        subprocess.run('python3 vtel.py iscsi dg d test_dg', shell=True)


    # 1.判断 HostGroup 是否存在，存在返回 None 2.遍历 Host 列表，若发现 Host 不存在返回 None 3.创建成功返回 True
    def test_create_hostgroup(self):
        # 已存在 HostGroup 测试用例
        with patch('builtins.print') as terminal_print:
            self.hostg.create_hostgroup('test_hg', ['test_host1'])
            terminal_print.assert_called_with('Fail! The HostGroup test_hg already existed.')
        # 提供的 host 列表中有不存在的 host 测试用例
        with patch('builtins.print') as terminal_print:
            self.hostg.create_hostgroup('test_hg1', ['test_host1', 'test_host0'])
            terminal_print.assert_called_with('Fail! Can\'t find test_host0.Please give the true name.')
        # 创建成功的测试用例
        assert self.hostg.create_hostgroup('test_hg1', ['test_host1'])
        # self.hostg.show_all_hostgroup()

    # 返回指定 DiskGroup ，如果为 DiskGroup 不存在，返回 None,否则返回该 DiskGroup
    def test_get_spe_hostgroup(self):
        # DiskGroup 不存在
        assert not self.hostg.get_spe_hostgroup('test_hg2')
        # DiskGroup 存在
        assert self.hostg.get_spe_hostgroup('test_hg1')

    # 该函数没有返回值，调用了本模块get_all_hostgroup()和sundry的show_iscsi_data()
    def test_show_all_hostgroup(self):
        assert self.hostg.show_all_hostgroup() is None

    # 该函数没有返回值，调用了本模块get_sep_hostgroup()和sundry的show_iscsi_data()
    def test_show_spe_hostgroup(self):
        assert self.hostg.show_spe_hostgroup('test_hg1') is None

    # 1.先检查 HostGroup 是否存在，不存在返回 None 2.再判断 HostGroup 是否已经配置在 Map里，已配置返回None 3.不满足前两个返回条件，删除后依然返回None
    # 这个方法无返回值
    def test_delete_hostgroup(self):
        with patch('builtins.print') as terminal_print:
            self.hostg.delete_hostgroup('test_hg2')
            terminal_print.assert_called_with('Fail! Can\'t find test_hg2')
        # print(f'判断条件：{self.js.check_value("Map", "test_dg")["result"]}')
        # 保留测试用例，该分支有bug
        with patch('builtins.print') as terminal_print:
            # print(f'判断条件：{self.js.check_value("Map","test_dg")["result"]}')
            self.map.show_all_map()
            self.hostg.delete_hostgroup('test_hg')
            terminal_print.assert_called_with('Fail! The hostgroup already map,Please delete the map')
        with patch('builtins.print') as terminal_print:
            self.hostg.delete_hostgroup('test_hg1')
            terminal_print.assert_called_with('Delete success!')

    # --------------------- add  --------------  2020.12.28

    def test_add_host(self):
        # with patch('builtins.print') as terminal_print:
        #     self.hostg.add_host('test_hg', ['test_host2'])
        #     terminal_print.assert_called_with()
        # 存在
        assert not self.hostg.add_host('test_hg', ['test_host2'])
        # 不存在
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.hostg.add_host('test_hg2', ['test_host2'])
                terminal_print.assert_called_with('不存在test_hg2可以去进行修改')
        assert exsinfo.type == SystemExit
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.hostg.add_host('test_hg', ['test_host'])
                terminal_print.assert_called_with('test_host已存在test_hg中')
        assert exsinfo.type == SystemExit
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.hostg.add_host('test_hg', ['test_host0'])
                terminal_print.assert_called_with('json文件中不存在test_host0，无法进行添加')
        assert exsinfo.type == SystemExit

    def test_remove_host(self):
        # with patch('builtins.print') as terminal_print:
        #     self.hostg.remove_host('test_hg', ['test_host2'])
        #     terminal_print.assert_called_with()
        # 存在
        assert not self.hostg.remove_host('test_hg', ['test_host2'])
        # 不存在
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.hostg.remove_host('test_hg2', ['test_host2'])
                terminal_print.assert_called_with('不存在test_hg2可以去进行修改')
        assert exsinfo.type == SystemExit
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.hostg.remove_host('test_hg', ['test_host0'])
                terminal_print.assert_called_with('test_hg中不存在成员test_host0，无法进行移除')
        assert exsinfo.type == SystemExit

    # 返回所有 HostGroup，如果为 HostGroup 空，返回{},否则返回 HostGroup 非空字典
    def test_get_all_hostgroup(self):
        # HostGroup 不为空
        assert self.hostg.get_all_hostgroup()
        # HostGroup 为空
        self.map.delete_map('map1')
        self.hostg.delete_hostgroup('test_hg')
        assert self.hostg.get_all_hostgroup() == {}


class TestMap:

    def setup_class(self):
        # 创建没有被使用过的disk
        subprocess.run('python3 vtel.py stor r c res_test1 -s 10m -a -num 1', shell=True)
        # 配置到没有被使用的diskgroup
        subprocess.run('python3 vtel.py iscsi dg c test_dg1 res_test1 ', shell=True)
        # 创建没有被使用的 host
        subprocess.run('python3 vtel.py iscsi h c test_host1 iqn.2020-04.feixitek.com:pytest0101', shell=True)
        # 配置到没有被使用的hostgroup
        subprocess.run('python3 vtel.py iscsi hg c test_hg1 test_host1', shell=True)

        subprocess.run('python3 vtel.py stor r c res_test -s 10m -a -num 1', shell=True)
        subprocess.run('python3 vtel.py iscsi d s', shell=True)
        subprocess.run('python3 vtel.py iscsi dg c test_dg res_test', shell=True)
        subprocess.run('python3 vtel.py iscsi h c test_host iqn.2020-04.feixitek.com:pytest01', shell=True)
        subprocess.run('python3 vtel.py iscsi hg c test_hg test_host', shell=True)
        self.map = iscsi.Map()
        subprocess.run('python3 vtel.py iscsi m c test_map -dg test_dg -hg test_hg', shell=True)

        subprocess.run('python3 vtel.py iscsi hg s ', shell=True)


    def teardown_class(self):
        subprocess.run('python3 vtel.py iscsi hg d test_hg -y', shell=True)
        subprocess.run('python3 vtel.py iscsi h d test_host -y', shell=True)
        subprocess.run('python3 vtel.py iscsi dg d test_dg -y', shell=True)
        subprocess.run('python3 vtel.py iscsi hg d test_hg1 -y', shell=True)
        subprocess.run('python3 vtel.py iscsi h d test_host1 -y', shell=True)
        subprocess.run('python3 vtel.py iscsi dg d test_dg1 -y', shell=True)
        try:
            subprocess.run('python3 vtel.py stor r d res_test -y', shell=True)
            subprocess.run('python3 vtel.py stor r d res_test1 -y', shell=True)

            execute_crm_cmd('crm res stop res_test')
            execute_crm_cmd('crm conf del res_test')
            execute_crm_cmd('crm res stop res_test1')
            execute_crm_cmd('crm conf del res_test1')
        except Exception:
            print('exception')
            # crm 模块中有个 delete_res 函数
            # from execute import crm
            # config_handler = crm.CRMConfig()
            # config_handler.delete_res('res_test')
        finally:
            subprocess.run('python3 vtel.py stor r d res_test -y', shell=True)
            subprocess.run('python3 vtel.py stor r d res_test1 -y', shell=True)

        subprocess.run('python3 vtel.py iscsi d s', shell=True)

    # 1.map 是否存在/hostgroup是否存在/diskgroup是否存在
    def test_pre_check_create_map(self):
        # map 已存在
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.map.pre_check_create_map('test_map', 'test_hg1', 'test_dg')
                terminal_print.assert_called_with('The Map "test_map" already existed.')
        assert exsinfo.type == SystemExit
        # hostgroup 不存在
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.map.pre_check_create_map('test_map1', 'test_hg0', 'test_dg')
                terminal_print.assert_called_with('Can\'t find test_hg0')
        assert exsinfo.type == SystemExit
        # diskgroup 不存在
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.map.pre_check_create_map('test_map1', 'test_hg', 'test_dg0')
                terminal_print.assert_called_with('Can\'t find test_dg0')
        assert exsinfo.type == SystemExit
        # 同时满足三个条件
        assert self.map.pre_check_create_map('test_map1', ['test_hg'], ['test_dg'])

    def test_get_target(self):
        # 检测该函数有返回值
        assert self.map.get_target() is not None

    @pytest.fixture(scope="class")
    def pre_test_create_map(self):
        # 创建没有被使用过的disk
        subprocess.run('python3 vtel.py stor r c res_test1 -s 10m -a -num 1', shell=True)
        # 配置到没有被使用的diskgroup
        subprocess.run('python3 vtel.py iscsi dg c test_dg1 res_test1 ', shell=True)
        # 创建没有被使用的 host
        subprocess.run('python3 vtel.py iscsi h c test_host1 iqn.2020-04.feixitek.com:pytest0101', shell=True)
        # 配置到没有被使用的hostgroup
        subprocess.run('python3 vtel.py iscsi hg c test_hg1 test_host1 ', shell=True)

    # 先调用pre_check_create_map()，这个函数已经在前面测试了
    # Q：已经被使用过的disk(ilu) 没有做处理？ A:已经被使用的disk 再映射到新的host会提示
    # 1.新建一个map，使用的是没有被使用的disk   create_iscsilogicalunit 没有对创建 iscsilogicalunit 失败做处理
    # 2.新建一个map，使用的是已经被使用的disk并映射到新的host上面
    # 3.同时符合以上两种条件内容的新建map
    def test_create_map(self):
        # 1.使用的是没有被使用的disk，调用 create_iscsilogicalunit，
        assert self.map.create_map('test_map1', ['test_hg'], ['test_dg'])
        # 2.使用的是已经被使用的disk并映射到新的host上面 调用 modify_iscsilogicalunit 这里会满足提示分支
        print('提示分支')
        assert self.map.create_map('test_map2', ['test_hg1'], ['test_dg'])
        # 3.同时符合以上两种条件内容的新建map
        assert self.map.create_map('test_map3', ['test_hg1'], ['test_dg', 'test_dg1'])

    # map 是否存在，存在返回非空列表[{map: map_data}, list_hg, list_dg],不存在返回 None
    def test_get_spe_map(self):
        # 不存在
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.map.get_spe_map('test_map0')
                terminal_print.assert_called_with('No map data')
        assert exsinfo.type == SystemExit
        # 存在
        assert self.map.get_spe_map('test_map1')

    # 该函数没有返回值，调用了本模块get_all_map()和sundry的show_iscsi_data()
    def test_show_all_map(self):
        assert self.map.show_all_map() is None

    def test_show_spe_map(self):
        assert self.map.show_spe_map('test_map1') is not None

    # 1.map 存在返回 True，不存在返回 None
    def test_pre_check_delete_map(self):
        # 不存在,warning_level = 1
        assert not self.map.pre_check_delete_map('test_map0')
        # 存在
        assert self.map.pre_check_delete_map('test_map1')

    # 1.使用pre_check_delete_map检查，map 不存在返回 None，删除成功返回 True
    def test_delete_map(self):
        # 不存在
        assert not self.map.delete_map('test_map0')
        # 删除成功
        assert self.map.delete_map('test_map3')

    # ------- add -------   2020.12.18

    # 检查列表的每个成员hg/dg是否存在
    def test_checkout_exist(self):
        # 调用 js 中的函数
        # 这里不使用 not 的原因是看不出返回值是False/None
        # 1.'HostGroup'类别，hg不存在
        assert self.map.checkout_exist('HostGroup', ['test_hg1', 'test_hg0']) is False
        # 1.'HostGroup'类别，hg存在
        assert self.map.checkout_exist('HostGroup', ['test_hg', 'test_hg1']) is None
        # 1.'DiskGroup'类别，hg不存在
        assert self.map.checkout_exist('DiskGroup', ['test_dg', 'test_dg0']) is False
        # 1.'DiskGroup'类别，dg存在
        assert self.map.checkout_exist('DiskGroup', ['test_dg', 'test_dg1']) is None

    # map modify -hg -a 调用
    def test_add_hg(self):
        # 成功增加
        assert self.map.add_hg('test_map1', ['test_hg1']) is None
        # 1.map 不存在
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.map.add_hg('map0', ['test_hg1'])
                terminal_print.assert_called_with('不存在map0可以去进行修改')
        assert exsinfo.type == SystemExit
        # 2.hg 已存在 map 中
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.map.add_hg('test_map1', ['test_hg'])
                terminal_print.assert_called_with('test_hg已存在test_map中')
        assert exsinfo.type == SystemExit
        # 3.hg 不存在 json 文件中
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.map.add_hg('test_map1', ['test_hg0'])
                terminal_print.assert_called_with('json文件中不存在test_hg0，无法进行添加')
        assert exsinfo.type == SystemExit

    # map modify -dg -a 调用
    # 1.map 是否存在
    # 2. dg 是否已存在在 map 中/ dg 是否存在 json 文件中
    def test_add_dg(self):
        # 成功增加
        assert self.map.add_dg('test_map2', ['test_dg1']) is None
        # 1.map 不存在
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.map.add_dg('map0', ['test_dg1'])
                terminal_print.assert_called_with('不存在map0可以去进行修改')
        assert exsinfo.type == SystemExit
        # 2.hg 已存在 map 中
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.map.add_dg('test_map2', ['test_dg'])
                terminal_print.assert_called_with('test_dg已存在test_map2中')
        assert exsinfo.type == SystemExit
        # 3.hg 不存在 json 文件中
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.map.add_dg('test_map2', ['test_dg0'])
                terminal_print.assert_called_with('json文件中不存在test_dg0，无法进行添加')
        assert exsinfo.type == SystemExit

    # map modify -hg -r 调用
    # 1.map 是否存在
    # 2.hg 是否存在于该 map 中
    def test_remove_hg(self):
        # 1.map 不存在
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.map.remove_hg('map0', ['test_hg1'])
                terminal_print.assert_called_with('不存在map0可以去进行修改')
        assert exsinfo.type == SystemExit
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.map.remove_hg('test_map1', ['test_hg0'])
                terminal_print.assert_called_with('test_map1中不存在成员test_hg0，无法进行移除')
        assert exsinfo.type == SystemExit
        # 成功移除
        # 移除 map 中 HostGroup 的某些 hg 值，该 map 不会被删除
        self.map.remove_hg('test_map1', ['test_hg'])
        list_hg = self.map.get_spe_map('test_map1')[1][0]
        assert list_hg[0] == 'test_hg1'
        # 移除 map 中 HostGroup 的全部 hg 值，该 map 被删除
        with patch('builtins.print') as terminal_print:
            self.map.remove_hg('test_map1', ['test_hg1'])
            terminal_print.assert_called_with('该test_map1已删除')

    # map modify -dg -r 调用
    # 1.map 是否存在
    # 2.dg 是否存在于该 map 中
    def test_remove_dg(self):
        # 1.map 不存在
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.map.remove_dg('map0', ['test_dg1'])
                terminal_print.assert_called_with('不存在map0可以去进行修改')
        assert exsinfo.type == SystemExit
        with pytest.raises(SystemExit) as exsinfo:
            with patch('builtins.print') as terminal_print:
                self.map.remove_dg('test_map2', ['test_dg0'])
                terminal_print.assert_called_with('test_map2中不存在成员test_dg0，无法进行移除')
        assert exsinfo.type == SystemExit
        # 成功移除
        # 移除 map 中 HostGroup 的某些 dg 值，该 map 不会被删除
        self.map.remove_dg('test_map2', ['test_dg'])
        list_dg = self.map.get_spe_map('test_map2')[2][0]
        assert list_dg[0] == 'test_dg1'
        # 移除 map 中 HostGroup 的全部 dg 值，该 map 被删除
        with patch('builtins.print') as terminal_print:
            self.map.remove_dg('test_map2', ['test_dg1'])
            terminal_print.assert_called_with('该test_map2已删除')

    # 获取 map 并返回，map 为空返回 {},不为空返回非空字典
    def test_get_all_map(self):
        # map 不为空
        assert self.map.create_map('test_map3', ['test_hg1'], ['test_dg', 'test_dg1'])
        assert self.map.get_all_map()
        # map 为空
        # self.map.delete_map('test_map1')
        # self.map.delete_map('test_map2')
        self.map.delete_map('test_map3')
        time.sleep(1)
        assert self.map.get_all_map() == {}

    # 该函数被其他函数调用 create_iSCSILogicalUnit
    def test_create_res(self):
        pass
        # assert self.map.create_res()

    # 获取已map的dg对应的hg
    # 无调用
    def test_get_hg_by_dg(self):
        pass
        # assert self.map.get_hg_by_dg('hg1')

    # 无调用
    def test_get_all_initiator(self):
        pass
        # for 循环调用了get_initiator
        # assert self.map.get_all_initiator(['hg1', 'hg2'])

    # 根据hg去获取hostiqn，返回由hostiqn组成的initiator
    # 调用该函数的 get_all_initiator 没有被调用，不测
    def test_get_initiator(self):
        pass
        # hg 不存在（不能传入不存在hg会抛出NoneType)
        # assert self.map.get_initiator('test_hg1') == ''
        # hg 存在
        # assert self.map.get_initiator('test_hg') == 'iqn.2020-04.feixitek.com:pytest01'

    # 无调用
    def test_get_all_disk(self):
        pass
        # assert self.map.get_all_disk(['dg1', 'dg2'])

    # 使用 linstro 命令,有可能返回{}或非空字典
    # 调用该函数的 get_all_disk 没有被调用，不测
    def test_get_disk_data(self):
        pass
        # 存在
        # assert self.map.get_disk_data('test_dg')
        # 不存在
        # assert self.map.get_disk_data('test_dg1') == {}


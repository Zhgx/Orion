from unittest.mock import patch

import pytest

from execute import stor
import sys
import io


# 判断 result ，非空返回 result ，result为空退出程序
def test_judge_result():
    assert stor.judge_result('SUCCESS') == {'rst': 'SUCCESS', 'sts': 0}
    assert stor.judge_result('WARNING') == {'rst': None, 'sts': 2}
    assert stor.judge_result('ERROR') == {'rst': 'ERROR', 'sts': 3}
    assert stor.judge_result('SUCCESS but WARNING') == {'rst': None, 'sts': 1}


# 提取 Description ，找不到返回 None
def test_get_err_detailes():
    data = '''ERROR:
Description:
    Resource definition 'res1' not found.
Cause:
    The specified resource definition 'res1' could not be found in the database'''
    assert stor.get_err_detailes(data) == "Resource definition 'res1' not found."


# 提取 Description 之后的 warnning message ，找不到返回 None
def test_get_war_mes():
    data = '''\x1b[1;33mWARNING:\n\x1b[0mDescription:\n    Deletion of storage pool 'pool_b' on node 'ubuntu' had no effect.\nCause:\n    Storage pool 'pool_b' on node 'ubuntu' does not exist.'''
    assert stor.get_war_mes(
        data) == "Description:\n    Deletion of storage pool 'pool_b' on node 'ubuntu' had no effect.\nCause:\n    Storage pool 'pool_b' on node 'ubuntu' does not exist."


def test_execute_linstor_cmd():
    assert stor.execute_linstor_cmd('ls') is not None


class TestNode:

    def setup_class(self):
        self.node = stor.Node()
        self.node_name = 'ubuntu'
        self.node_ip = '10.203.1.76'

    def test_delete_node(self):
        sys.stdout = io.StringIO()
        # 成功
        self.node.delete_node(self.node_name)
        assert 'SUCCESS' in sys.stdout.getvalue()
        # 删除不存在节点
        with patch('builtins.print') as terminal_print:
            self.node.delete_node('window')
        terminal_print.assert_called_with(
            '''FAIL\nDescription:\n    Deletion of node 'window' had no effect.\nCause:\n    Node 'window' does not exist.\nDetails:\n    Node: window\n''')

    def test_create_node(self):
        # 成功
        sys.stdout = io.StringIO()
        self.node.create_node(self.node_name, self.node_ip, 'Combined')
        assert 'SUCCESS' in sys.stdout.getvalue()
        # type 不正确
        with patch('builtins.print') as terminal_print:
            self.node.create_node(self.node_name, self.node_ip, 'xxx')
            terminal_print.assert_called_with('node type error,choose from ''Combined',
                                              'Controller', 'Auxiliary', 'Satellite''')
        # 已创建
        with pytest.raises(SystemExit) as exsinfo:
            self.node.create_node(self.node_name, self.node_ip, 'Combined')
        assert exsinfo.type == SystemExit

    def test_show_one_node(self):
        sys.stdout = io.StringIO()
        # 存在
        self.node.show_one_node(self.node_name)
        assert 'ubuntu' in sys.stdout.getvalue()
        self.node.show_one_node(self.node_name, '')
        assert 'ubuntu' in sys.stdout.getvalue()
        # 不存在
        with patch('builtins.print') as terminal_print:
            self.node.show_one_node('windows')
            terminal_print.assert_called_with('The node does not exist')

    def test_show_all_node(self):
        sys.stdout = io.StringIO()
        self.node.show_all_node()
        assert 'ubuntu' in sys.stdout.getvalue()
        self.node.show_all_node('')
        assert 'ubuntu' in sys.stdout.getvalue()


class TestStoragePool:

    def setup_class(self):
        self.sp = stor.StoragePool()
        self.node_name = 'ubuntu'

    def test_create_storagepool_lvm(self):
        sys.stdout = io.StringIO()
        # 成功
        self.sp.create_storagepool_lvm(self.node_name, 'sp_pytest_lvm', 'drbdpool')
        assert 'SUCCESS' in sys.stdout.getvalue()
        # 失败
        with pytest.raises(SystemExit) as exsinfo:
            self.sp.create_storagepool_lvm('window', 'sp_pytest_lvm', 'drbdpool')
        assert exsinfo.type == SystemExit

    def test_create_storagepool_thinlv(self):
        sys.stdout = io.StringIO()
        self.sp.create_storagepool_thinlv(self.node_name, 'sp_pytest_thinlv', 'drbdpool/thinlv_test')
        assert 'SUCCESS' in sys.stdout.getvalue()
        self.sp.delete_storagepool(self.node_name, 'sp_pytest_thinlv')
        with pytest.raises(SystemExit) as exsinfo:
            self.sp.create_storagepool_thinlv('window', 'sp_pytest_thinlv', 'drbdpool/thinlv_test')
        assert exsinfo.type == SystemExit

    def test_show_all_sp(self):
        sys.stdout = io.StringIO()
        self.sp.show_all_sp()
        assert 'sp_pytest_lvm' in sys.stdout.getvalue()
        self.sp.show_all_sp('')
        assert 'sp_pytest_lvm' in sys.stdout.getvalue()

    def test_show_one_sp(self):
        sys.stdout = io.StringIO()
        # 存在
        self.sp.show_one_sp('sp_pytest_lvm')
        assert 'sp_pytest_lvm' in sys.stdout.getvalue()
        self.sp.show_one_sp('sp_pytest_lvm', '')
        assert 'sp_pytest_lvm' in sys.stdout.getvalue()

        # 不存在
        with patch('builtins.print') as terminal_print:
            self.sp.show_one_sp('sp_pytest_lvm0')
            terminal_print.assert_called_with('The storagepool does not exist')

    def test_delete_storagepool(self):
        sys.stdout = io.StringIO()
        # 成功
        self.sp.delete_storagepool(self.node_name, 'sp_pytest_lvm')
        assert 'SUCCESS' in sys.stdout.getvalue()
        # 删除不存在storagepool
        # 1.
        with pytest.raises(SystemExit) as exsinfo:
            self.sp.delete_storagepool(self.node_name, 'sp_pytest_lvm0')
        assert exsinfo.type == SystemExit
        # 2.
        with pytest.raises(SystemExit) as exsinfo:
            self.sp.delete_storagepool('window', 'sp_pytest_lvm')
        assert exsinfo.type == SystemExit


class TestResource:

    def setup_class(self):
        self.node_name = 'ubuntu'
        try:
            self.sp = stor.StoragePool()
            self.sp.create_storagepool_lvm(self.node_name, 'pytest_sp1', 'drbdpool')
        except Exception:
            pass
        self.res = stor.Resource()

    # 不能删掉pytest_sp1这个storagepool会影响iscsi disk 的创建
    # def teardown_class(self):
    #     try:
    #         self.sp = stor.StoragePool()
    #         self.sp.delete_storagepool(self.node_name, 'pytest_sp1')
    #     except Exception:
    #         pass

    # 收集输入的参数，进行处理
    # 这里考虑 node 列表和 storagepool 列表为空的情况么（commands 模块传值时有做判断）
    def test_collect_args(self):
        assert self.res.collect_args([self.node_name], ['pytest_sp1']) == {'ubuntu': 'pytest_sp1'}
        assert self.res.collect_args([self.node_name, 'window'], ['pytest_sp1', 'pytest_sp2']) == {
            'ubuntu': 'pytest_sp1', 'window': 'pytest_sp2'}

    # 成功返回 True 有可能返回None 失败返回 result
    def test_linstor_create_rd(self):
        # 成功
        assert self.res.linstor_create_rd('pytest_res') is True
        # 重复创建，失败
        with pytest.raises(SystemExit) as exsinfo:
            self.res.linstor_create_rd('pytest_res')
        assert exsinfo.type == SystemExit

    # 成功返回 True 有可能返回None 失败返回 result
    def test_linstor_create_vd(self):
        assert self.res.linstor_create_vd('pytest_res', '10m') is True
        # vd 可以重名创建，创建失败时删除同名的rd,同时也会把该vd删掉
        # assert self.res.linstor_create_vd('pytest_res', '10m') == 3

    # 成功返回空字典，失败返回 {节点：错误原因}
    def test_execute_create_res(self):
        assert self.res.execute_create_res('pytest_res', self.node_name, 'pytest_sp1') == {}
        # 超时会抛异常SystemExit

    # 无返回值 主要采用 execute_linstor_cmd
    def test_show_all_res(self):
        sys.stdout = io.StringIO()
        self.res.show_all_res()
        assert 'pytest_res' in sys.stdout.getvalue()
        self.res.show_all_res('')
        assert 'pytest_res' in sys.stdout.getvalue()

    # 无返回值 主要采用 execute_linstor_cmd
    def test_show_one_res(self):
        sys.stdout = io.StringIO()
        self.res.show_one_res('pytest_res')
        assert 'pytest_res' in sys.stdout.getvalue()
        self.res.show_one_res('pytest_res', '')
        assert 'pytest_res' in sys.stdout.getvalue()
        # 不存在
        with patch('builtins.print') as terminal_print:
            self.res.show_one_res('pytest_res0')
            terminal_print.assert_called_with('The resource does not exist')

    # 无返回值 主要采用 execute_linstor_cmd
    def test_delete_resource_des(self):
        sys.stdout = io.StringIO()
        self.res.delete_resource_des(self.node_name, 'pytest_res')
        assert 'SUCCESS' in sys.stdout.getvalue()
        # 不存在
        # 1.
        with pytest.raises(SystemExit) as exsinfo:
            self.res.delete_resource_des(self.node_name, 'pytest_res0')
        assert exsinfo.type == SystemExit
        # 2.
        with pytest.raises(SystemExit) as exsinfo:
            self.res.delete_resource_des('window', 'pytest_res')
        assert exsinfo.type == SystemExit

    # 无返回值 主要采用 execute_linstor_cmd
    def test_delete_resource_all(self):
        self.res.execute_create_res('pytest_res', self.node_name, 'pool_a')
        sys.stdout = io.StringIO()
        self.res.delete_resource_all('pytest_res')
        assert 'SUCCESS' in sys.stdout.getvalue()
        # 不存在 (抛warning）
        # self.res.delete_resource_all('pytest_res0')

    # 成功返回 True 失败返回 result / return ('The resource already exists')
    def test_create_res_auto(self):
        assert self.res.create_res_auto('pytest_res', '10m', 1) is True
        # 重复创建，失败测试用例
        with pytest.raises(SystemExit) as exsinfo:
            self.res.create_res_auto('pytest_res', '10m', 1)
        assert exsinfo.type == SystemExit

    # 无返回值
    def test_linstor_delete_rd(self):
        assert self.res.linstor_delete_rd('pytest_res') is None

    # 成功 True 已存在返回 'The resource already exists' 失败返回 dict_all_fail
    def test_create_res_manual(self):
        assert self.res.create_res_manual('pytest_res', '10m', [self.node_name], ['pytest_sp1']) is True
        # 重复创建，失败测试用例
        # rd 不能重复创建，在创建 res 会有判断，如果 rd 创建存在问题会影响接下来的条件判断结构，导致代码覆盖率不能如预期
        with pytest.raises(SystemExit) as exsinfo:
            self.res.create_res_manual('pytest_res', '10m', [self.node_name], ['pytest_sp1'])
        assert exsinfo.type == SystemExit
        self.res.linstor_delete_rd('pytest_res')

    # 无返回值
    def test_create_res_diskless(self):
        self.res.linstor_create_rd('pytest_res')
        self.res.linstor_create_vd('pytest_res', '10m')
        assert self.res.create_res_diskless([self.node_name], 'pytest_res') is None
        # 重复创建，失败测试用例
        with pytest.raises(SystemExit) as exsinfo:
            self.res.create_res_diskless([self.node_name], 'pytest_res')
        assert exsinfo.type == SystemExit
        self.res.linstor_delete_rd('pytest_res')

    def test_add_mirror_auto(self):
        self.res.linstor_create_rd('pytest_res')
        self.res.linstor_create_vd('pytest_res', '10m')
        self.res.execute_create_res('pytest_res', self.node_name, 'pytest_sp1')
        # 会创建失败因为只有一个node
        sys.stdout = io.StringIO()
        self.res.add_mirror_auto('pytest_res', 1)
        assert 'FAIL' in sys.stdout.getvalue()
        self.res.linstor_delete_rd('pytest_res')

    def test_add_mirror_manual(self):
        self.res.linstor_create_rd('pytest_res')
        self.res.linstor_create_vd('pytest_res', '10m')
        self.res.execute_create_res('pytest_res', self.node_name, 'pytest_sp1')
        # 同一个节点上创建不了镜像
        with pytest.raises(SystemExit) as exsinfo:
            self.res.add_mirror_manual('pytest_res', ['ubuntu'], ['pytest_sp'])
        assert exsinfo.type == SystemExit
        self.res.linstor_delete_rd('pytest_res')

from unittest.mock import patch

import pytest

import sundry
import consts


# 函数不存在
# def test_get_function_name():
#     pass

@pytest.mark.skip(reason="no way of currently testing this")
def test_get_answer():
    # 该函数参数为 input
    pass
    # assert sundry.get_answer() is not None


def test_create_transaction_id():
    assert sundry.create_transaction_id() is not None


def test_create_oprt_id():
    assert sundry.create_oprt_id() is not None


def test_get_username():
    assert sundry.get_username() == 'root'


def test_get_hostname():
    assert sundry.get_hostname() == 'ubuntu'


def test_get_path():
    assert 'vplx' in sundry.get_path()


def test_re_findall():
    re_string = r'iqn\.*[a-zA-Z0-9.:-]+'
    iqn = 'iqn.2020.test:pytest01'
    assert sundry.re_findall(re_string, iqn) == ['iqn.2020.test:pytest01']


def test_re_search():
    re_string = 'string_test_001'
    string = 'string_test_001_string_test_002'
    assert sundry.re_search(re_string, string) == 'string_test_001'


def test_show_iscsi_data():
    list_header = ["ResourceName", "Path"]
    data = {"pytest_disk": "/dev/sdb1"}
    assert sundry.show_iscsi_data(list_header, data)


def test_show_map_data():
    list_header = ["MapName", "HostGroup", "DiskGroup"]
    data = {'map1': {"HostGroup": ['hg1', 'hg2'], "DiskGroup": ['dg1', 'dg2']}}
    assert sundry.show_map_data(list_header, data)._field_names == ["MapName", "HostGroup", "DiskGroup"]
    assert sundry.show_map_data(list_header, data)._rows == [['map1', 'hg1 hg2', 'dg1 dg2']]

# 函数已删除
# def test_show_linstor_data():
#     head = ['node', 'node type', 'res num', 'stp num', 'addr', 'status']
#     data = [['ubuntu', 'COMBINED', 6, 3, '10.203.1.76:3366', 'pytest']]
#     assert sundry.show_linstor_data(head, data)._field_names == ['node', 'node type', 'res num', 'stp num', 'addr',
#                                                                  'status']
#     assert sundry.show_linstor_data(head, data)._rows == [['ubuntu', 'COMBINED', 6, 3, '10.203.1.76:3366', 'pytest']]


def test_change_pointer():
    sundry.change_pointer(12345)
    assert consts.glo_log_id() == 12345


def test_execute_cmd():
    assert 'sundry.py' in sundry.execute_cmd('ls')


def test_prt():
    with patch('builtins.print') as terminal_print:
        sundry.prt('test_prt')
        terminal_print.assert_called_with('test_prt')


def test_prt_log():
    with patch('builtins.print') as terminal_print:
        sundry.prt_log('test_prt_log', 0)
        terminal_print.assert_called_with('test_prt_log')
    with pytest.raises(SystemExit) as exsinfo:
        with patch('builtins.print') as terminal_print:
            sundry.prt_log('test_prt_log', 2)
            terminal_print.assert_called_with('test_prt_log')
    assert exsinfo.type == SystemExit


# -----------------  add  ------------   2020.12.28

# 获取 show_map_data 函数的返回结果再做处理
def test_show_spe_map_data():
    header_host = ["HostGroup", "HostName", "IQN"]
    data = [['test_hg', 'test_host', 'iqn'], ['test_hg1', 'test_host1', 'iqn1']]
    assert sundry.show_spe_map_data(header_host, data)._field_names == ["HostGroup", "HostName", "IQN"]
    assert sundry.show_spe_map_data(header_host, data)._rows == [['test_hg', 'test_host', 'iqn'],
                                                                 ['test_hg1', 'test_host1', 'iqn1']]


# 装饰器函数
@pytest.mark.skip(reason="no way of currently testing this")
def test_deco_json_operation():
    pass


def test_remove_list():
    list_data = sundry.remove_list(['123', '123', '4', '5', '5'], ['123'])
    list_data.sort()
    assert ['4', '5'] == list_data


def test_append_list():
    list_data = sundry.append_list(['1', '1', '3', '5', '1'], ['2', '2', '3'])
    list_data.sort()
    assert ['1', '2', '3','5'] == list_data


@pytest.mark.skip(reason="no way of currently testing this")
def test_confirm_modify():
    pass
    # 该函数参数为 input
    # assert sundry.confirm_modify('y') is None
    # assert sundry.confirm_modify('yes') is None
    # assert sundry.confirm_modify('Y') is None
    # assert sundry.confirm_modify('YES') is None
    # with pytest.raises(SystemExit) as exsinfo:
    #     with patch('builtins.print') as terminal_print:
    #         sundry.confirm_modify('no')
    #         terminal_print.assert_called_with('中断修改，退出')
    # assert exsinfo.type == SystemExit


# 装饰器函数
@pytest.mark.skip(reason="no way of currently testing this")
def test_deco_db_insert():
    pass


# 装饰器函数
@pytest.mark.skip(reason="no way of currently testing this")
def test_deco_color():
    pass

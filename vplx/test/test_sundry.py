import sundry
import consts


def test_get_function_name():
    pass


def test_get_answer():
    pass
    # assert sundry.get_answer() != None


def test_create_transaction_id():
    assert sundry.create_transaction_id() != None


def test_create_oprt_id():
    assert sundry.create_oprt_id() != None


def test_get_username():
    assert sundry.get_username() == 'root'


def test_get_hostname():
    assert sundry.get_hostname() == 'ubuntu'


def test_get_path():
    assert sundry.get_path() != None


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
    data = {"pytest_map": ['hg1', 'dg1']}
    assert sundry.show_map_data(list_header, data) != None


def test_show_linstor_data():
    head = ['node', 'node type', 'res num', 'stp num', 'addr', 'status']
    data = [['ubuntu', 'COMBINED', 6, 3, '10.203.1.76:3366', 'pytest']]
    assert sundry.show_linstor_data(head, data) != None


def test_change_pointer():
    sundry.change_pointer(12345)
    assert consts.glo_log_id() == 12345


def test_execute_cmd():
    assert 'sundry.py' in sundry.execute_cmd('ls')


def test_prt():
    assert sundry.prt('test_prt') == None


def test_prt_log():
    assert sundry.prt_log('test_prt_log', 0) == None


# -----------------  add  ------------   2020.12.28

def test_show_spe_map_data():
    assert True


def test_deco_json_operation():
    assert True


def test_remove_list():
    assert True


def test_append_list():
    assert True


def test_confirm_modify():
    assert True


def test_deco_db_insert():
    assert True


def test_deco_color():
    assert True

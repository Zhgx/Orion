from execute import stor


def test_judge_result():
    assert stor.judge_result('SUCCESS') == {'rst': 'SUCCESS', 'sts': 0}
    assert stor.judge_result('WARNING') == {'rst': None, 'sts': 2}
    assert stor.judge_result('ERROR') == {'rst': 'ERROR', 'sts': 3}
    assert stor.judge_result('SUCCESS but WARNING') == {'rst': None, 'sts': 1}


def test_get_err_detailes():
    data = '''ERROR:
Description:
    Resource definition 'res1' not found.
Cause:
    The specified resource definition 'res1' could not be found in the database'''
    assert stor.get_err_detailes(data) == "Resource definition 'res1' not found."


def test_get_war_mes():
    data = '''\x1b[1;33mWARNING:\n\x1b[0mDescription:\n    Deletion of storage pool 'pool_b' on node 'ubuntu' had no effect.\nCause:\n    Storage pool 'pool_b' on node 'ubuntu' does not exist.'''
    assert stor.get_war_mes(data) == "Description:\n    Deletion of storage pool 'pool_b' on node 'ubuntu' had no effect.\nCause:\n    Storage pool 'pool_b' on node 'ubuntu' does not exist."


def test_execute_linstor_cmd():
    pass
import consts


def test_init():
    """测试 consts 初始化方法"""
    consts.init()
    assert consts._GLOBAL_DICT != None


def test_set_value():
    """测试 consts 设置 value 方法"""
    consts.set_value('test_key', 'test_value')
    assert consts._GLOBAL_DICT['test_key'] == 'test_value'


def test_get_value():
    """测试 consts 获取 value 方法"""
    assert consts.get_value('test_key') == 'test_value'


# def test_set_glo_log():
#     consts.set_glo_log('test_log')
#     assert consts._GLOBAL_DICT['LOG'] == 'test_log'


<<<<<<< HEAD
def test_set_glo_db():
    """测试 consts 设置 log 数据库方法"""
    consts.set_glo_db('test_db')
    assert consts._GLOBAL_DICT['LOG_DB'] == 'test_db'


def test_set_glo_rpl():
    """测试 consts 设置是否为 replay 模式方法"""
    consts.set_glo_rpl('test_rpl')
    assert consts._GLOBAL_DICT['RPL'] == 'test_rpl'
=======



>>>>>>> b78e6cb5f618d5ddec071cdb27972707d55b5a74


def test_set_glo_tsc_id():
    """测试 consts 设置 TSC_ID 方法"""
    consts.set_glo_tsc_id('test_tsc_id')
    assert consts._GLOBAL_DICT['TSC_ID'] == 'test_tsc_id'


def test_set_glo_log_id():
    """测试 consts 设置 LOG_ID 方法"""
    consts.set_glo_log_id('test_log_id')
    assert consts._GLOBAL_DICT['LOG_ID'] == 'test_log_id'


# def test_set_glo_log_switch():
#     """测试 consts 设置 LOG_SWITCH 方法"""
#     consts.set_glo_log_switch('test_switch')
#     assert consts._GLOBAL_DICT['LOG_SWITCH'] == 'test_switch'


def test_set_glo_gui_tid():
    """测试 consts 设置 GUI_TID 方法"""
    consts.set_glo_gui_tid('test_tid')
    assert consts._GLOBAL_DICT['GUI_TID'] == 'test_tid'


<<<<<<< HEAD
def test_glo_gui_tid():
    """测试 consts 获取 GUI tid 方法"""
    assert consts.glo_gui_tid() == 'test_tid'
=======
>>>>>>> b78e6cb5f618d5ddec071cdb27972707d55b5a74


# def test_glo_log():
#     assert consts.glo_log() == 'test_log'


<<<<<<< HEAD
def test_glo_db():
    """测试 consts 获取 LOG 数据库方法"""
    assert consts.glo_db() == 'test_db'
=======
>>>>>>> b78e6cb5f618d5ddec071cdb27972707d55b5a74


def test_glo_rpl():
    """测试 consts 获取是否为 replay 模式方法"""
    assert consts.glo_rpl() == 'test_rpl'


def test_glo_tsc_id():
    """测试 consts 获取 TSC_ID 方法"""
    assert consts.glo_tsc_id() == 'test_tsc_id'


def test_glo_log_id():
    """测试 consts 获取 Log id 方法"""
    assert consts.glo_log_id() == 'test_log_id'


# def test_glo_log_switch():
#     assert consts.glo_log_switch() == 'test_switch'
def test_glo_str():
    """测试 consts 获取 str 方法"""
    consts.set_value('STR', 'test_str')
    assert consts.glo_str() == 'test_str'


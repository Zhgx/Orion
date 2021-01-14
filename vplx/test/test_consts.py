import consts


def test_init():
    consts._init()
    assert consts._GLOBAL_DICT != None


def test_set_value():
    consts.set_value('test_key', 'test_value')
    assert consts._GLOBAL_DICT['test_key'] == 'test_value'


def test_get_value():
    assert consts.get_value('test_key') == 'test_value'


# def test_set_glo_log():
#     consts.set_glo_log('test_log')
#     assert consts._GLOBAL_DICT['LOG'] == 'test_log'


def test_set_glo_db():
    consts.set_glo_db('test_db')
    assert consts._GLOBAL_DICT['LOG_DB'] == 'test_db'


def test_set_glo_rpl():
    consts.set_glo_rpl('test_rpl')
    assert consts._GLOBAL_DICT['RPL'] == 'test_rpl'


def test_set_glo_tsc_id():
    consts.set_glo_tsc_id('test_tsc_id')
    assert consts._GLOBAL_DICT['TSC_ID'] == 'test_tsc_id'


def test_set_glo_log_id():
    consts.set_glo_log_id('test_log_id')
    assert consts._GLOBAL_DICT['LOG_ID'] == 'test_log_id'


def test_set_glo_log_switch():
    consts.set_glo_log_switch('test_switch')
    assert consts._GLOBAL_DICT['LOG_SWITCH'] == 'test_switch'

def test_set_glo_gui_tid():
    consts.set_glo_gui_tid('test_tid')
    assert consts._GLOBAL_DICT['GUI_TID'] == 'test_tid'


def test_glo_gui_tid():
    assert consts.glo_gui_tid() == 'test_tid'


# def test_glo_log():
#     assert consts.glo_log() == 'test_log'


def test_glo_db():
    assert consts.glo_db() == 'test_db'


def test_glo_rpl():
    assert consts.glo_rpl() == 'test_rpl'


def test_glo_tsc_id():
    assert consts.glo_tsc_id() == 'test_tsc_id'


def test_glo_log_id():
    assert consts.glo_log_id() == 'test_log_id'


def test_glo_log_switch():
    assert consts.glo_log_switch() == 'test_switch'
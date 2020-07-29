"""
Global constants for vtel
"""

VERSION = "1.1.0"


class ExitCode(object):
    OK = 0
    UNKNOWN_ERROR = 1
    ARGPARSE_ERROR = 2
    OBJECT_NOT_FOUND = 3
    OPTION_NOT_SUPPORTED = 4
    ILLEGAL_STATE = 5
    CONNECTION_ERROR = 20
    CONNECTION_TIMEOUT = 21
    UNEXPECTED_REPLY = 22
    API_ERROR = 10
    NO_SATELLITE_CONNECTION = 11


class ReplayExit(Exception):
    "replay时，输出日志中的异常信息后，此次replay事务也随之停止"
    pass


def _init():
    global _global_dict
    _global_dict = {}
    _global_dict['LOG_ID'] = 0
    _global_dict['RPL'] = 'no'
    _global_dict['LOG_SWITCH'] = 'yes'

def set_value(key, value):
    """ 定义一个全局变量 """
    _global_dict[key] = value


def get_value(key, dft_val = None):
    """ 获得一个全局变量,不存在则返回默认值 """
    try:
        return _global_dict[key]
    except KeyError:
        return dft_val


def set_glo_log(value):
    set_value('LOG', value)


def get_glo_log():
    return get_value('LOG')



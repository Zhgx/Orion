import colorama as ca
import consts
from functools import wraps
import prettytable
import traceback


def equal(data1, data2):
    try:
        assert data1 == data2
        return True
    except:
        return False


def str_in(data1, data2):
    try:
        assert data1 in data2
        return True
    except:
        return False


def type_int(data):
    try:
        assert isinstance(data, int)
        return True
    except:
        return False


def type_str(data):
    try:
        assert isinstance(data, str)
        return True
    except:
        return False


def type_list(data):
    try:
        assert isinstance(data, list)
        return True
    except:
        return False


def type_dict(data):
    try:
        assert isinstance(data, dict)
        return True
    except:
        return False


def get_data_type(str):
    if str:
        try:
            str = eval(str)
        except Exception:  # 正常字符串：NameError，'011'：SyntaxError
            pass
    return type(str)


def get_assert_table(list_header, list_data):
    table = prettytable.PrettyTable()
    table.field_names = list_header
    for i in list_data:
        table.add_row(i)
    return table


def rt_dec(assert_type, select_key=None, str_part=None, times=1):
    def decorate(func):
        @wraps(func)
        def wrapper(self, *args):
            RPL = consts.glo_rpl()
            RG = consts.glo_rg()
            func_result = func(self, *args)
            if RPL == 'yes' and RG == 'yes':
                list_assert = []
                logdb = consts.glo_db()
                if times == 1:
                    log_id = 0
                else:
                    log_id = consts.glo_log_id() - 1

                if select_key:
                    id_result = logdb.get_id(
                        consts.glo_tsc_id(), select_key, log_id)
                else:
                    id_result = logdb.get_id(
                        consts.glo_tsc_id(), func.__name__, log_id)

                log_result = logdb.get_oprt_result(
                    id_result['oprt_id'])['result']
                func_result_type = get_data_type(func_result)
                log_result_type = get_data_type(log_result)
                list_assert.append(log_result_type)
                list_assert.append(func_result_type)
                if func_result_type == log_result_type:
                    list_assert.append('T')
                else:
                    list_assert.append('F')

                if assert_type == 'equal':
                    list_assert.append('equal')
                    assert_result = equal(str(func_result), log_result)

                elif assert_type == 'str_in':
                    list_assert.append('str_in')
                    assert_result = str_in(str_part, log_result)

                elif assert_type == 'type_list':
                    list_assert.append('type_list')
                    assert_result = type_list(log_result)
                else:
                    assert_result = False

                if assert_result:
                    list_assert.append(f"{ca.Fore.GREEN + 'T' + ca.Style.RESET_ALL}")
                else:
                    list_assert.append(f"{ca.Fore.RED + 'F' + ca.Style.RESET_ALL}")
                list_assert.append(func.__name__)

                traceback_data = f'File" {traceback.extract_stack()[-2][0]}" line {traceback.extract_stack()[-2][1]}'
                list_assert.append(traceback_data)
                consts.set_glo_rg_data(list_assert)

            return func_result
        return wrapper
    return decorate

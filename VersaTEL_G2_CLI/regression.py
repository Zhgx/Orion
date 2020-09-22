import colorama as ca
import consts
from functools import wraps


def equal(data1, data2):
    try:
        print('data1:',data1,type(data1))
        print('data2:',data2,type(data2))
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



def rt_dec(str,select_key = None, str_part = None,):
    def decorate(func):
        @wraps(func)
        def wrapper(self, *args):
            RPL = consts.glo_rpl()
            result_a = func(self, *args)
            if RPL == 'yes':
                logdb = consts.glo_db()
                if select_key:
                    id_result = logdb.get_id(consts.glo_tsc_id(), select_key, 0)
                else:
                    print(func.__name__)
                    print(consts.glo_log_id())
                    id_result = logdb.get_id(consts.glo_tsc_id(), func.__name__,0)
                result_b = logdb.get_oprt_result(id_result['oprt_id'])['result']
                if result_b:
                    try:
                        result_b = eval(result_b)
                    except NameError:
                        pass
                if str == 'equal':
                    assert_result = equal(result_a, result_b)

                elif str == 'str_in':
                    assert_result = str_in(str_part,result_a)

                elif str == 'type_list':
                    assert_result = type_list(result_a)
                else:
                    assert_result = False

                if assert_result:
                    print(f"{func.__name__}断言结果：{ca.Fore.GREEN + 'T' + ca.Style.RESET_ALL}")
                else:
                    print(f"{func.__name__}断言结果：{ca.Fore.RED + 'F' + ca.Style.RESET_ALL}")
            return result_a
        return wrapper
    return decorate

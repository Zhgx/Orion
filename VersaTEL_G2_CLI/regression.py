import colorama as ca
import consts
from functools import wraps


def equal(data1, data2):
    try:
        assert data1 == data2
        print('')
        return True
    except:
        print('')
        print('断言方式：equal')
        print('data1:',data1,type(data1))
        print('data2:',data2,type(data2))
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



def rt_dec(str,select_key=None, str_part=None, times=1):
    def decorate(func):
        @wraps(func)
        def wrapper(self, *args):
            RPL = consts.glo_rpl()
            RG = consts.glo_rg()
            result_a = func(self, *args)
            if RPL == 'yes' and RG == 'yes':
                logdb = consts.glo_db()
                if times == 1:
                    log_id = 0
                else:
                    log_id = consts.glo_log_id() - 1

                if select_key:
                    id_result = logdb.get_id(consts.glo_tsc_id(), select_key, log_id)
                else:
                    id_result = logdb.get_id(consts.glo_tsc_id(), func.__name__, log_id)
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

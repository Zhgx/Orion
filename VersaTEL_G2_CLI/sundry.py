# coding:utf-8
import socket
import signal
import time
import os
import getpass
import traceback
import re
import prettytable
import sys
from random import shuffle
import subprocess
from functools import wraps
import colorama as ca

import consts
import execute


# Connect to the socket server and transfer data, and finally close the
# connection.
def send_via_socket(data):
    ip = "10.203.1.151"
    port = 12144

    client = socket.socket()
    client.connect((ip, port))
    judge_conn = client.recv(8192).decode()
    print(judge_conn)
    client.send(b'database')
    client.recv(8192)
    client.sendall(data)
    client.recv(8192)
    client.send(b'exit')
    client.close()

def record_exception(func):
    """
    Decorator
    Get exception, throw the exception after recording
    :param func:Command binding function
    """
    def wrapper(self,*args):
        try:
            return func(self,*args)
        except Exception as e:
            self.logger.write_to_log('DATA','debug','exception','', str(traceback.format_exc()))
            raise e
    return wrapper


def comfirm_del(type):
    """
    Decorator providing confirmation of deletion function.
    :param func: Function to delete linstor resource
    """
    def decorate(func):
        def wrapper(self,*args):
            cli_args = args[0]
            if cli_args.yes:
                func(self,*args)
            else:
                print(f"Are you sure you want to delete this {type}? If yes, enter 'y/yes'")
                answer = get_answer()
                if answer in ['y', 'yes']:
                    func(self,*args)
                else:
                    prt_log('Delete canceled',0)
        return wrapper
    return decorate


def get_answer():
    logger = consts.glo_log()
    rpl = consts.glo_rpl()
    logdb = consts.glo_db()
    transaction_id = consts.glo_tsc_id()

    if rpl == 'no':
        answer = input()
        logger.write_to_log('DATA', 'input', 'user_input', 'confirm deletion', answer)
    else:
        time,answer = logdb.get_anwser(transaction_id)
        if not time:
            time = ''
        print(f'RE:{time:<20} 用户输入: {answer}')
    return answer





def timeout(seconds,error_message = 'Funtion call timed out'):
    def decorated(func):
        def _handled_timeout(signum,frame):
            raise TimeoutError(error_message)

        def wrapper(*args,**kwargs):
            signal.signal(signal.SIGALRM, _handled_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args,**kwargs)
            finally:
                signal.alarm(0)
            return result
        return wrapper
    return decorated


def create_transaction_id():
    return int(time.time())

def create_oprt_id():
    time_stamp = str(create_transaction_id())
    str_list = list(time_stamp)
    shuffle(str_list)
    return ''.join(str_list)

def get_username():
    return getpass.getuser()

def get_hostname():
    return socket.gethostname()

# Get the path of the program
def get_path():
    return os.getcwd()


def re_findall(re_string, tgt_string):
    logger = consts.glo_log()
    re_ = re.compile(re_string)
    oprt_id = create_oprt_id()
    logger.write_to_log('OPRT', 'regular', 'findall', oprt_id, {'re': re_, 'string': tgt_string})
    re_result = re_.findall(tgt_string)
    logger.write_to_log('DATA', 'regular', 'findall', oprt_id, re_result)
    return re_result


def re_search(re_string, tgt_stirng):
    logger = consts.glo_log()
    re_ = re.compile(re_string)
    oprt_id = create_oprt_id()
    logger.write_to_log('OPRT','regular','search',oprt_id, {'re':re_,'string':tgt_stirng})
    re_result = re_.search(tgt_stirng).group()
    logger.write_to_log('DATA', 'regular', 'search', oprt_id, re_result)
    return re_result


def show_iscsi_data(list_header,dict_data):
    table = prettytable.PrettyTable()
    table.field_names = list_header
    if dict_data:
        for i,j in dict_data.items():
            data_one = [i,(' '.join(j) if isinstance(j,list) == True else j)]
            table.add_row(data_one)
    else:
        pass
    return table

def show_map_data(list_header,dict_data):
    table = prettytable.PrettyTable()
    table.field_names = list_header
    if dict_data:
        # {map1:[hg1,dg1] => [map1,hg1,dg1]}
        for i, j in dict_data.items():
            j.insert(0,i)
            table.add_row(j)
    else:
        pass
    return table


def show_linstor_data(list_header,list_data):
    table = prettytable.PrettyTable()
    table.field_names = list_header
    if list_data:
        for i in list_data:
            table.add_row(i)
    else:
        pass
    return table


def change_pointer(new_id):
    consts.set_glo_log_id(new_id)

def cmd_decorator(type):
    def decorate(func):
        @wraps(func)
        def wrapper(cmd):
            RPL = consts.glo_rpl()
            oprt_id = create_oprt_id()
            if RPL == 'no':
                logger = consts.glo_log()
                logger.write_to_log('DATA', 'STR', func.__name__, '', oprt_id)
                logger.write_to_log('OPRT', 'cmd', type, oprt_id, cmd)
                result_cmd = func(cmd)
                logger.write_to_log('DATA', 'cmd', type, oprt_id, result_cmd)
                return result_cmd
            else:
                logdb = consts.glo_db()
                id_result = logdb.get_id(consts.glo_tsc_id(), func.__name__)
                cmd_result = logdb.get_oprt_result(id_result['oprt_id'])
                if type == 'crm':
                    result = eval(cmd_result['result'])
                else:
                    result = cmd_result['result']
                print('*')
                print(f"RE:{id_result['time']} 执行系统命令：\n{cmd}")
                print(f"RE:{cmd_result['time']} 系统命令结果：\n{cmd_result['result']}")
                if id_result['db_id']:
                    change_pointer(id_result['db_id'])
            return result
        return wrapper
    return decorate


@cmd_decorator('sys cmd')
def execute_cmd(cmd, timeout=60):
    p = subprocess.Popen(cmd, stderr=subprocess.STDOUT, stdout=subprocess.PIPE, shell=True)
    t_beginning = time.time()
    seconds_passed = 0
    while True:
        if p.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning
        if timeout and seconds_passed > timeout:
            p.terminate()
            raise TimeoutError(cmd, timeout)
        time.sleep(0.1)
    output = p.stdout.read().decode()
    return output


@cmd_decorator('crm')
def execute_crm_cmd(cmd, timeout=60):
    """
    Execute the command cmd to return the content of the command output.
    If it times out, a TimeoutError exception will be thrown.
    cmd - Command to be executed
    timeout - The longest waiting time(unit:second)
    """
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    t_beginning = time.time()
    seconds_passed = 0
    while True:
        if p.poll() is not None:
            break
        seconds_passed = time.time() - t_beginning
        if timeout and seconds_passed > timeout:
            p.terminate()
            raise TimeoutError(cmd, timeout)
        time.sleep(0.1)
    out, err = p.communicate()
    if len(out) > 0:
        out = out.decode()
        output = {'sts': 1, 'rst': out}
        return output
    if len(err) > 0:
        err = err.decode()
        output = {'sts': 0, 'rst': err}
        return output
    if out == b'':  # 需要再考虑一下 res stop 执行成功没有返回，stop失败也没有返回（无法判断stop成不成功）
        out = out.decode()
        output = {'sts': 1, 'rst': out}
        return output


# def get_cmd_result(unique_str, cmd, oprt_id):
#     logger = consts.glo_log()
#     RPL = consts.glo_rpl()
#     if RPL == 'no':
#         logger.write_to_log('DATA', 'STR', unique_str, '', oprt_id)
#         logger.write_to_log('OPRT', 'cmd', '', oprt_id, cmd)
#         result_cmd = execute_cmd(cmd)
#         logger.write_to_log('DATA', 'cmd', '', oprt_id, result_cmd)
#         return result_cmd
#     elif RPL == 'yes':
#         logdb = consts.glo_db()
#         id_result = logdb.get_id(consts.glo_tsc_id(), unique_str)
#         cmd_result = logdb.get_oprt_result(id_result['oprt_id'])
#         print('*')
#         print(f"RE:{id_result['time']} 执行系统命令：\n{cmd}")
#         print(f"RE:{cmd_result['time']} 系统命令结果：\n{cmd_result['result']}")
#         if id_result['db_id']:
#             change_pointer(id_result['db_id'])
#         return cmd_result['result']


# def get_crm_cmd_result(unique_str, cmd, oprt_id):
#     logger = consts.glo_log()
#     RPL = consts.glo_rpl()
#     if RPL == 'no':
#         logger.write_to_log('DATA', 'STR', unique_str, '', oprt_id)
#         logger.write_to_log('OPRT', 'cmd', 'iscsi', oprt_id, cmd)
#         result_cmd = execute_crm_cmd(cmd)
#         logger.write_to_log('DATA', 'cmd', 'iscsi', oprt_id, result_cmd)
#         return result_cmd
#     elif RPL == 'yes':
#         logdb = consts.glo_db()
#         id_result = logdb.get_id(consts.glo_tsc_id(), unique_str)
#         cmd_result = logdb.get_cmd_result(oprt_id)
#         if cmd_result:
#             result = eval(cmd_result['result'])
#         else:
#             result = None
#         print('*')
#         print(f"RE:{id_result['time']} 执行系统命令：\n{cmd}")
#         print(f"RE:{cmd_result['time']} 系统命令结果：\n{cmd_result['result']}")
#         if id_result['db_id']:
#             change_pointer(id_result['db_id'])
#         return result




def prt(str, warning_level=0):
    if isinstance(warning_level, int):
        warning_str = '*' * warning_level
    else:
        warning_str = ''
    rpl = consts.glo_rpl()

    if rpl == 'no':
        print(str)

    else:
        if warning_level == 'exception':
            print(' exception infomation '.center(105, '*'))
            print(str)
            print(f'{" exception infomation ":*^105}', '\n')
            return

        db = consts.glo_db()
        time,cmd_output = db.get_cmd_output(consts.glo_tsc_id())
        if not time:
            time = ''
        print(f'RE:{time:<20} 日志记录输出：{warning_str:<4}\n{cmd_output}')
        print(f'RE:{"":<20} 此次执行输出：{warning_str:<4}\n{str}')


def prt_log(str, warning_level):
    """
    print, write to log and exit.
    :param logger: Logger object for logging
    :param print_str: Strings to be printed and recorded
    """
    logger = consts.glo_log()
    rpl = consts.glo_rpl()
    if rpl == 'yes':
        prt(str, warning_level)
    elif rpl == 'no':
        prt(str, warning_level)

    if warning_level == 0:
        logger.write_to_log('INFO', 'info', 'finish','output',str)
    elif warning_level == 1:
        logger.write_to_log('INFO', 'warning', 'fail', 'output', str)
    elif warning_level == 2:
        logger.write_to_log('INFO', 'error', 'exit', 'output', str)
        # print(f'{"":-^{format_width}}','\n')
        # sys.exit()


def pwe(str, warning_level):
    rpl = consts.glo_rpl()
    prt_log(str,warning_level)

    if warning_level == 2:
        if rpl == 'no':
            sys.exit()
        else:
            raise consts.ReplayExit



def color_data(func):
    """
    装饰器，给特定的linstor数据进行着色
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args):
        status_true = ['UpToDate', 'Online', 'Ok', 'InUse']
        data = func(*args)
        for lst in data:
            if lst[-1] in status_true:
                lst[-1] = ca.Fore.GREEN + lst[-1] + ca.Style.RESET_ALL
            else:
                lst[-1] = ca.Fore.RED + lst[-1] + ca.Style.RESET_ALL
        return data
    return wrapper




def json_operate_decorator(str):
    """
    Decorator providing confirmation of deletion function.
    :param func: Function to delete linstor resource
    """
    def decorate(func):
        @wraps(func)
        def wrapper(self, *args):
            RPL = consts.glo_rpl()
            if RPL == 'no':
                logger = consts.glo_log()
                oprt_id = create_oprt_id()
                logger.write_to_log('DATA', 'STR', func.__name__, '', oprt_id)
                logger.write_to_log('OPRT', 'JSON', func.__name__, oprt_id, args)
                result = func(self,*args)
                logger.write_to_log('DATA', 'JSON', func.__name__, oprt_id,result)
            else:
                logdb = consts.glo_db()
                id_result = logdb.get_id(consts.glo_tsc_id(), func.__name__)
                json_result = logdb.get_oprt_result(id_result['oprt_id'])
                result = eval(json_result['result'])
                print(f"RE:{id_result['time']} {str}：\n{result}")
                if id_result['db_id']:
                    change_pointer(id_result['db_id'])
            return result
        return wrapper
    return decorate


